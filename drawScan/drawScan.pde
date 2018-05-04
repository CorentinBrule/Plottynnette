import controlP5.*;

import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;

/**
 * Loading Tabular Data
 * by Daniel Shiffman.  
 * 
 * This example demonstrates how to use loadTable()
 * to retrieve data from a CSV file and make objects 
 * from that data.
 *
 * Here is what the CSV looks like:
 *
 */

ControlP5 cp5;
// An Array of Bubble objects
IntList all_x;
IntList all_y;
IntList all_val;
// A Table object
Table table;
int countVal;
int mult;

int decalX_pair;
int decalX_impair;
float sizeX_pair;
float sizeX_impair;
boolean colorize_line;

int contrast_min;
int contrast_max;

PGraphics scan;
PGraphics pair;
PGraphics impair;

void setup() {
  size(800, 800, P2D);
  oscP5 = new OscP5(this, 12000);
  myRemoteLocation = new NetAddress("127.0.0.1", 12000);

  all_x = new IntList();
  all_y = new IntList();
  all_val = new IntList();
  mult = 1;

  colorize_line=true;

  loadData();
  //createData();
  scan = createGraphics(297, 420);
  pair = createGraphics(297, 420);
  impair = createGraphics(297, 420);
  scan.noStroke();
  cp5 = new ControlP5(this);
  ui();
}

void draw() {
  pair.beginDraw();
  pair.clear();
  pair.noStroke();
  impair.beginDraw();
  impair.clear();
  impair.noStroke();
  int rowCount = 0;
  for (TableRow row : table.rows()) {

    int x = row.getInt("x");
    int y = row.getInt("y");
    int val = row.getInt("value");

    float mapped_val = map(val, contrast_min, contrast_max, 0, 255);
    //float mapped_val = val
    if (y % 2 == 0) {
      //x*=sizeX_pair;
      //x+=decalX_pair;
      if (colorize_line) {
        pair.fill(mapped_val, 0, 0); //R
      } else {
        pair.fill(mapped_val);
      }
      pair.rect(x*mult, y*mult, mult, mult);
    } else {
      //x*=sizeX_impair;
      //x+=decalX_impair;
      if (colorize_line) {
        impair.fill(0, 0, mapped_val); //B
      } else {
        impair.fill(mapped_val);
      }
      impair.rect(x*mult, y*mult, mult, mult);
    }



    rowCount++;
  }
  pair.endDraw();
  impair.endDraw();
  scan.beginDraw();
  scan.clear();
  scan.image(pair, decalX_pair*mult, 0, pair.width*sizeX_pair, pair.height);
  scan.image(impair, decalX_impair*mult, 0, impair.width*sizeX_impair, impair.height);
  scan.endDraw();
  image(scan, 0, 0, scan.width*2, scan.height*2);
}


void loadData() {
  // Load CSV file into a Table object
  // "header" option indicates the file has a header row
  table = loadTable("data.csv", "header");

  // The size of the array of Bubble objects is determined by the total number of rows in the CSV
  // You can access iterate over all the rows in a table
}

void createData() {

  table = new Table();
  table.addColumn("x", Table.INT);
  table.addColumn("y", Table.INT);
  table.addColumn("value", Table.INT);
}

void oscEvent(OscMessage oscMessage) {
  /* print the address pattern and the typetag of the received OscMessage */
  TableRow newRow = table.addRow();
  int x = oscMessage.get(0).intValue();
  int y = oscMessage.get(1).intValue();
  int value = oscMessage.get(2).intValue();
  newRow.setInt("x", x);
  newRow.setInt("y", y);
  newRow.setInt("value", value);
  println(x, y, value);
}
