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
 x,y,diameter,name
 160,103,43.19838,Happy
 372,137,52.42526,Sad
 273,235,61.14072,Joyous
 121,179,44.758068,Melancholy
 */

// An Array of Bubble objects
IntList all_x;
IntList all_y;
IntList all_val;
// A Table object
Table table;
int countVal;
int mult;



void setup() {
  size(800, 800);
  noStroke();
  all_x = new IntList();
  all_y = new IntList();
  all_val = new IntList();
  mult = 2;

  loadData();
  /*
  countVal = 0;
   for (int x = 0 ; x < all_x.size() ; x++){
   for(int y = 0 ; y < all_y.size() ; y++){
   fill(all_val.get(countVal));
   rect(all_x.get(x),all_y.get(y),mult,mult);
   countVal++;
   }
   }*/
}

void draw() {
  int rowCount = 0;
  for (TableRow row : table.rows()) {
    // You can access the fields via their column name (or index)
    /*
    all_x.append(row.getInt("x"));
     all_y.append(row.getInt("y"));
     all_val.append(row.getInt("value"));
     // Make a Bubble object out of the data read
     */
    int x = row.getInt("x");
    int y = row.getInt("y");
    int val = row.getInt("value");

    float mapped_val = map(val, 160, 180, 0, 255);
    //float mapped_val = val
    if (y % 2 == 0) {
      x-=12;
      fill(mapped_val, 0, 0); //R
      fill(mapped_val);
    } else {
      x+=11;
      fill(0, 0, mapped_val); //V
      fill(mapped_val);
    }

    rect(x*mult, y*mult, mult, mult);

    rowCount++;
  }
}


void loadData() {
  // Load CSV file into a Table object
  // "header" option indicates the file has a header row
  table = loadTable("data.csv", "header");

  // The size of the array of Bubble objects is determined by the total number of rows in the CSV
  // You can access iterate over all the rows in a table
}
