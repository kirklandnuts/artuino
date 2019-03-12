int KEY = 2;                 // Connect Touch sensor on Digital Pin 2

void setup()
{
  Serial.begin(19200);
  pinMode(KEY, INPUT);       //Set touch sensor pin to input mode
  Serial.println("setup complete");
}


void loop()
{
  int touching = digitalRead(KEY); // 0 when off, 1 when on
  Serial.print("digitalRead(KEY): ");
  Serial.println(touching); 
  delay(100);
}
