/* Akeru.h - sendSingleValues.ino
 *
 * SIGFOX Example
 *
 * How to send a single analog value on the Sigfox network
 */

#include <Akeru.h>

// TD1208 Sigfox module IO definition
/*   Snootlab device | TX | RX
               Akeru | D4 | D5
               Akene | D5 | D4
            Breakout | your pick */
#define TX 4
#define RX 5

// Sigfox instance management
Akeru akeru(RX, TX);


long randNumber;

void setup()
{
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  Serial.println("Starting...");

  // Check TD1208 communication
  if (!akeru.begin())
  {
    Serial.println("TD1208 KO");
    while(1);
  }

  // initialize a random seed
  randomSeed(analogRead(0));
  //akeru.echoOn(); // uncomment this line to see AT commands
}

void loop()
{
  randNumber = random(100);

  // Trace on serial console
  Serial.println(randNumber);

  // convert to hexadecimal before sending
  String data = akeru.toHex(randNumber);

  // akeru.sendPayload() returns 0 if message failed.
  if (akeru.sendPayload(data))
  {
    Serial.println("Message sent !");
  }

  // Wait for 10 minutes.
  // Note that delay(600000) will block the Arduino (bug in delay()?)
  for (int second = 0; second < 600; second++)
  {
    delay(1000);
  }
}
