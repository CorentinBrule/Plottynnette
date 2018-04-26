import controlP5.*;

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

void setup() {
  size(800, 800, P2D);
  
  all_x = new IntList();
  all_y = new IntList();
  all_val = new IntList();
  mult = 1;

  colorize_line=true;

  loadData();
  scan = createGraphics(297,420);
  scan.noStroke();
  cp5 = new ControlP5(this);
  ui();
}

void draw() {
  scan.beginDraw();
  scan.clear();
  scan.noStroke();
  int rowCount = 0;
  for (TableRow row : table.rows()) {
    
    int x = row.getInt("x");
    int y = row.getInt("y");
    int val = row.getInt("value");

    float mapped_val = map(val, contrast_min, contrast_max, 0, 255);
    //float mapped_val = val
    if (y % 2 == 0) {
      x*=sizeX_pair;
      x+=decalX_pair;
      if (colorize_line) {
        
        scan.fill(mapped_val, 0, 0); //R
      } else {
        scan.fill(mapped_val);
      }
    } else {
      x*=sizeX_impair;
      x+=decalX_impair;
      if (colorize_line) {
        scan.fill(0, 0, mapped_val); //V
      } else {
        scan.fill(mapped_val);
      }
    }

    scan.rect(x*mult, y*mult, mult, mult);

    rowCount++;
  }
  scan.endDraw();
  image(scan,0,0,scan.width*2,scan.height*2);
}


void loadData() {
  // Load CSV file into a Table object
  // "header" option indicates the file has a header row
  table = loadTable("data.csv", "header");

  // The size of the array of Bubble objects is determined by the total number of rows in the CSV
  // You can access iterate over all the rows in a table
}
