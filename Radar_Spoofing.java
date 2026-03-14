import processing.serial.*;

Serial myPort;
String data = "";
int distance = 0;

float baseLat = 28.6139;
float baseLon = 77.2090;

PVector[] drones = new PVector[5];
float sweepAngle = PI; // Starts from left end
int spoofTimer = 0;

float[] spoofedLat = new float[4];
float[] spoofedLon = new float[4];

void setup() {
  size(600, 400);
  println(Serial.list());
  myPort = new Serial(this, "COM21", 9600); // Update COM port as needed
  myPort.bufferUntil('\n');

  for (int i = 0; i < drones.length; i++) {
    drones[i] = new PVector();
  }

  generateSpoofedLocations();
  textAlign(CENTER);
  textSize(12);
}

void draw() {
  background(0);
  translate(width / 2, height);  // Radar base at bottom center

  drawRadar();
  drawSweep();

  // Real drone position (from ultrasonic)
  float realLat = baseLat + distance * 0.00001;
  float realLon = baseLon + distance * 0.00001;
  drones[0].x = map(realLat, baseLat - 0.03, baseLat + 0.03, -250, 250);
  drones[0].y = -map(realLon, baseLon, baseLon + 0.05, 0, 250);
  drawDrone(drones[0], 1, true);

  // Fake drones
  for (int i = 1; i < drones.length; i++) {
    drones[i].x = map(spoofedLat[i - 1], baseLat - 0.03, baseLat + 0.03, -250, 250);
    drones[i].y = -map(spoofedLon[i - 1], baseLon, baseLon + 0.05, 0, 250);
    drawDrone(drones[i], i + 1, false);
  }

  // Sweep movement (semi-circle)
  sweepAngle += 0.008;
  if (sweepAngle > TWO_PI) sweepAngle = PI;

  // Update fake drone positions every 6 seconds
  if (millis() - spoofTimer > 6000) {
    generateSpoofedLocations();
    spoofTimer = millis();
  }
}

void drawRadar() {
  stroke(0, 255, 0);
  noFill();

  // Semi-circle arcs
  arc(0, 0, 500, 500, PI, TWO_PI);
  arc(0, 0, 350, 350, PI, TWO_PI);
  arc(0, 0, 200, 200, PI, TWO_PI);

  // Base dot
  fill(0, 255, 0);
  ellipse(0, 0, 10, 10);

  // Direction lines
  for (int i = 0; i <= 6; i++) {
    float angle = map(i, 0, 6, PI, TWO_PI);
    float x = 250 * cos(angle);
    float y = 250 * sin(angle);
    line(0, 0, x, y);
  }
}

void drawSweep() {
  stroke(0, 255, 0, 100);
  float x = 250 * cos(sweepAngle);
  float y = 250 * sin(sweepAngle);
  line(0, 0, x, y);
}

void drawDrone(PVector pos, int id, boolean isReal) {
  if (isReal) {
    fill(0, 255, 0); // Green
  } else {
    fill(255, 0, 0); // Red
  }
  ellipse(pos.x, pos.y, 10, 10);
  fill(255);
  text("Drone " + id, pos.x, pos.y - 12);
}

void serialEvent(Serial port) {
  data = trim(port.readStringUntil('\n'));
  if (data != null && data.length() > 0) {
    distance = int(data);
  }
}

void generateSpoofedLocations() {
  for (int i = 0; i < 4; i++) {
    float latOffset = random(0.01, 0.03) * (random(1) < 0.5 ? -1 : 1);
    float lonOffset = random(0.01, 0.05);
    spoofedLat[i] = baseLat + latOffset;
    spoofedLon[i] = baseLon + lonOffset;
  }
}
