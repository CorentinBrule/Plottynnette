char cmd;

void setup() {

  Serial.begin(9600);
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);
  cmd = 'Z';
}

void loop() {
  int valeur = analogRead(A0);

  if (Serial.available() > 0) {
    cmd = Serial.read();
    switch (cmd) {
      case 'L':
        Serial.println(valeur);
        delay(10);
        //Serial.println("ok");
        cmd = 'Z';
        break;

    }
  
  }

}
