/**
 * ESP32 BLE Command Handler Firmware - FIXED VERSION
 * 
 * Commands are received via BLE WRITE characteristic as UTF-8 strings.
 * 
 * FIXES:
 * - Separated heartbeat LED from controlled pins
 * - Fixed command processing to avoid interrupt conflicts
 * - Pins stay in their set state permanently
 * 
 * Protocol format:
 *   gpio_set:pin=X,value=Y
 *   gpio_mode:pin=X,mode=MODE
 *   gpio_get:pin=X
 *   status
 * 
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>

// BLE UUIDs (must match Python SDK)
#define SERVICE_UUID        "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define WRITE_CHAR_UUID     "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

// Device configuration
#define DEVICE_NAME         "ESP32-LinkBrain"
#define HEARTBEAT_LED       2  // Usually pin 2, but use constant
#define HEARTBEAT_INTERVAL  3000         // Blink every 3 seconds

// Connection state
bool deviceConnected = false;

// Command buffer (safer than processing in interrupt)
String globalCommand = "";
volatile bool commandReceived = false;

// Pin state tracking (for status command)
struct PinState {
  int mode;    // INPUT=1, OUTPUT=2, INPUT_PULLUP=3, -1=unset
  int value;   // Last written value (0 or 1)
};

PinState pinStates[40];  // ESP32 has up to 40 GPIO pins

/**
 * Parse parameter from command string
 * Example: "pin=2,value=1" -> getParam("pin") returns "2"
 */
String getParam(String command, String paramName) {
  int startIdx = command.indexOf(paramName + "=");
  if (startIdx == -1) return "";
  
  startIdx += paramName.length() + 1;
  int endIdx = command.indexOf(",", startIdx);
  
  if (endIdx == -1) {
    return command.substring(startIdx);
  }
  return command.substring(startIdx, endIdx);
}

/**
 * Parse and execute GPIO set command
 * Format: gpio_set:pin=X,value=Y
 */
void handleGpioSet(String params) {
  String pinStr = getParam(params, "pin");
  String valueStr = getParam(params, "value");
  
  if (pinStr.length() == 0 || valueStr.length() == 0) {
    Serial.println("ERROR: gpio_set missing parameters");
    return;
  }
  
  int pin = pinStr.toInt();
  int value = valueStr.toInt();
  
  // Validate pin range
  if (pin < 0 || pin >= 40) {
    Serial.printf("ERROR: Invalid pin %d\n", pin);
    return;
  }
  
  if (pin == HEARTBEAT_LED) {
    Serial.printf("WARNING: Pin %d is reserved for heartbeat LED\n", pin);
    Serial.println("ERROR: Cannot control reserved pin");
    return;
  }
  
  // Validate value
  if (value != 0 && value != 1) {
    Serial.printf("ERROR: Invalid value %d (must be 0 or 1)\n", value);
    return;
  }
  
  // Ensure pin is configured as output
  if (pinStates[pin].mode != OUTPUT) {
    pinMode(pin, OUTPUT);
    pinStates[pin].mode = OUTPUT;
    Serial.printf("Auto-configured pin %d as OUTPUT\n", pin);
  }
  
  // Set the pin and save state
  digitalWrite(pin, value);
  pinStates[pin].value = value;
  
  Serial.printf("OK: gpio_set pin=%d value=%d\n", pin, value);
}

/**
 * Parse and execute GPIO mode command
 * Format: gpio_mode:pin=X,mode=MODE
 * Modes: input, output, input_pullup
 */
void handleGpioMode(String params) {
  String pinStr = getParam(params, "pin");
  String modeStr = getParam(params, "mode");
  
  if (pinStr.length() == 0 || modeStr.length() == 0) {
    Serial.println("ERROR: gpio_mode missing parameters");
    return;
  }
  
  int pin = pinStr.toInt();
  
  // Validate pin range
  if (pin < 0 || pin >= 40) {
    Serial.printf("ERROR: Invalid pin %d\n", pin);
    return;
  }
  
  // Don't allow mode change on heartbeat LED
  if (pin == HEARTBEAT_LED) {
    Serial.printf("WARNING: Pin %d is reserved for heartbeat LED\n", pin);
    Serial.println("ERROR: Cannot configure reserved pin");
    return;
  }
  
  // Parse mode
  int mode;
  if (modeStr == "output") {
    mode = OUTPUT;
  } else if (modeStr == "input") {
    mode = INPUT;
  } else if (modeStr == "input_pullup") {
    mode = INPUT_PULLUP;
  } else {
    Serial.printf("ERROR: Invalid mode '%s'\n", modeStr.c_str());
    return;
  }
  
  // Configure pin
  pinMode(pin, mode);
  pinStates[pin].mode = mode;
  
  Serial.printf("OK: gpio_mode pin=%d mode=%s\n", pin, modeStr.c_str());
}

/**
 * Parse and execute GPIO get command
 * Format: gpio_get:pin=X
 */
void handleGpioGet(String params) {
  String pinStr = getParam(params, "pin");
  
  if (pinStr.length() == 0) {
    Serial.println("ERROR: gpio_get missing pin parameter");
    return;
  }
  
  int pin = pinStr.toInt();
  
  // Validate pin range
  if (pin < 0 || pin >= 40) {
    Serial.printf("ERROR: Invalid pin %d\n", pin);
    return;
  }
  
  // Read current pin value
  int value = digitalRead(pin);
  pinStates[pin].value = value;
  
  Serial.printf("OK: gpio_get pin=%d value=%d\n", pin, value);
}

/**
 * Handle status command
 * Returns device information
 */
void handleStatus() {
  Serial.println("OK: status");
  Serial.println("  Device: ESP32-LinkBrain");
  Serial.println("  BLE: Connected");
  Serial.printf("  Free heap: %d bytes\n", ESP.getFreeHeap());
  Serial.printf("  Uptime: %lu ms\n", millis());
  Serial.printf("  Heartbeat LED: Pin %d\n", HEARTBEAT_LED);
  
  // Report configured pins
  Serial.println("  Configured pins:");
  for (int i = 0; i < 40; i++) {
    if (pinStates[i].mode != -1 && i != HEARTBEAT_LED) {
      String modeStr = (pinStates[i].mode == OUTPUT) ? "OUTPUT" :
                       (pinStates[i].mode == INPUT) ? "INPUT" : "INPUT_PULLUP";
      Serial.printf("    Pin %d: %s, value=%d\n", i, modeStr.c_str(), pinStates[i].value);
    }
  }
}

/**
 * Main command dispatcher
 * Parses command type and routes to appropriate handler
 */
void processCommand(String command) {
  command.trim();
  
  if (command.length() == 0) {
    return;
  }
  
  Serial.printf("\n>>> Received: '%s'\n", command.c_str());
  
  // Split command into type and parameters
  int colonIdx = command.indexOf(':');
  String cmdType;
  String params = "";
  
  if (colonIdx != -1) {
    cmdType = command.substring(0, colonIdx);
    params = command.substring(colonIdx + 1);
  } else {
    cmdType = command;
  }
  
  // Route to handler
  if (cmdType == "gpio_set") {
    handleGpioSet(params);
  } 
  else if (cmdType == "gpio_mode") {
    handleGpioMode(params);
  } 
  else if (cmdType == "gpio_get") {
    handleGpioGet(params);
  } 
  else if (cmdType == "status") {
    handleStatus();
  }
  else if (cmdType == "blink") {
    // Test command - blinks heartbeat LED only
    Serial.println("OK: blink (test command)");
    for(int i = 0; i < 5; i++) {
      digitalWrite(HEARTBEAT_LED, HIGH);
      delay(200);
      digitalWrite(HEARTBEAT_LED, LOW);
      delay(200);
    }
  }
  else {
    Serial.printf("WARNING: Unknown command type '%s'\n", cmdType.c_str());
  }
}

/**
 * BLE Server callbacks - handle connection lifecycle
 */
class ServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("\n=== BLE Device Connected ===");
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("\n=== BLE Device Disconnected ===");
    Serial.println("Restarting advertising...");
    
    // Allow next connection
    pServer->getAdvertising()->start();
  }
};

/**
 * BLE Characteristic callbacks - handle incoming commands
 * FIXED: Just set flag, don't process in interrupt
 */
class CharacteristicCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String value = pCharacteristic->getValue();
    if (value.length() > 0) {
      // Just capture the command and set flag
      noInterrupts();
      globalCommand = String(value.c_str());
      commandReceived = true;
      interrupts();
    }
  }
};

/**
 * Initialize BLE server and characteristics
 */
void setupBLE() {
  Serial.println("Initializing BLE...");
  
  BLEDevice::init(DEVICE_NAME);
  
  // Create BLE server
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());
  
  // Create BLE service
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  // Create WRITE characteristic
  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
    WRITE_CHAR_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );
  
  pCharacteristic->setCallbacks(new CharacteristicCallbacks());
  
  // Start service
  pService->start();
  
  // Configure advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  
  // Start advertising
  BLEDevice::startAdvertising();
  
  Serial.println("BLE ready!");
  Serial.printf("Device name: %s\n", DEVICE_NAME);
  Serial.printf("Heartbeat LED: Pin %d (reserved)\n", HEARTBEAT_LED);
  Serial.println("Waiting for connections...");
}

/**
 * Arduino setup
 */
void setup() {
  Serial.begin(115200);
  delay(1000);  // Wait for serial to stabilize
  
  Serial.println("\n\n=================================");
  Serial.println("ESP32 LinkBrain Command Handler");
  Serial.println("Version: 1.1 (Fixed)");
  Serial.println("=================================\n");
  
  // Initialize pin state tracking
  for (int i = 0; i < 40; i++) {
    pinStates[i].mode = -1;
    pinStates[i].value = 0;
  }
  
  // Configure heartbeat LED (separate from user pins)
  pinMode(HEARTBEAT_LED, OUTPUT);
  digitalWrite(HEARTBEAT_LED, LOW);
  pinStates[HEARTBEAT_LED].mode = OUTPUT;
  pinStates[HEARTBEAT_LED].value = 0;
  
  // Initialize BLE
  setupBLE();
  
  Serial.println("\nReady to receive commands!");
  Serial.println("Supported commands:");
  Serial.println("  gpio_set:pin=X,value=Y");
  Serial.println("  gpio_mode:pin=X,mode=MODE");
  Serial.println("  gpio_get:pin=X");
  Serial.println("  status");
  Serial.printf("\nNote: Pin %d is reserved for heartbeat LED\n", HEARTBEAT_LED);
  Serial.println("Use other pins for your devices!\n");
}

/**
 * Arduino main loop
 * FIXED: Proper command processing outside interrupt
 * FIXED: Heartbeat doesn't interfere with user pins
 */
void loop() {
  // Process pending commands (outside interrupt context)
  if (commandReceived) {
    // Safely capture command and reset flag
    noInterrupts();
    String commandToProcess = globalCommand;
    commandReceived = false;
    interrupts();
    
    // Process command in main loop (safe)
    processCommand(commandToProcess);
  }
  
  // Non-blocking heartbeat on DEDICATED LED pin
  static unsigned long lastHeartbeat = 0;
  unsigned long currentMillis = millis();
  
  if (deviceConnected && (currentMillis - lastHeartbeat >= HEARTBEAT_INTERVAL)) {
    // Quick blink to show device is alive
    digitalWrite(HEARTBEAT_LED, HIGH);
    delay(50);  // Very short blink
    digitalWrite(HEARTBEAT_LED, LOW);
    lastHeartbeat = currentMillis;
  }
  
  // Give BLE stack time to process
  yield();
}
