void ui() {

  cp5.addSlider("decalX_pair")
    .setPosition(width-150, 10)
    .setRange(-30, 30)
    .setValue(-11)
    ;
  cp5.addSlider("decalX_impair")
    .setPosition(width-150, 30)
    .setRange(-30, 30)
    .setValue(11)
    ;

  cp5.addSlider("sizeX_pair")
    .setPosition(width-150, 60)
    .setRange(0, 2)
    .setValue(1)
    ;
  cp5.addSlider("sizeX_impair")
    .setPosition(width-150, 80)
    .setRange(0, 2)
    .setValue(1)
    ;
  cp5.addToggle("colorize_line")
    .setPosition(width-150, 100)
    .setSize(50, 20)
    .setValue(true)
    .setMode(ControlP5.SWITCH)
    ;

  cp5.addSlider("contrast_min")
    .setPosition(width-150, 140)
    .setRange(0, 255)
    .setValue(160)
    ;
  cp5.addSlider("contrast_max")
    .setPosition(width-150, 160)
    .setRange(0, 255)
    .setValue(180)
    ;
}
