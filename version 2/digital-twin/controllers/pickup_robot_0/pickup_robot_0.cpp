// File:          pikup_robot_controller.cpp
// Date:
// Description:
// Author:
// Modifications:

// You may need to add webots include files such as
// <webots/DistanceSensor.hpp>, <webots/Motor.hpp>, etc.
// and/or to add some other includes
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <webots/DistanceSensor.hpp>
#include <iostream>
#include <cmath>
#define TIME_STEP 64
#define lBL_Strength_ON 750
#define lBL_Strength_OFF 0
// All the webots classes are defined in the "webots" namespace
using namespace webots;


int main(int argc, char **argv) {
  // create the Robot instance.
  // Robot *robot = new Robot();

  Supervisor *supervisor = new Supervisor();
  Node *Pickup_node = supervisor->getSelf();
  Node *PR_LED_0 = supervisor->getFromDef("PR_0_LED_0");
  Node *PR_LED_1 = supervisor->getFromDef("PR_0_LED_1");
  Node *PR_LED_2 = supervisor->getFromDef("PR_0_LED_2");
  Node *PR_LED_3 = supervisor->getFromDef("PR_0_LED_3");
  
  DistanceSensor *PR_DS_0 = supervisor->getDistanceSensor("PR_0_DS_0");
  DistanceSensor *PR_DS_1 = supervisor->getDistanceSensor("PR_0_DS_1");
  DistanceSensor *PR_DS_2 = supervisor->getDistanceSensor("PR_0_DS_2");
  DistanceSensor *PR_DS_3 = supervisor->getDistanceSensor("PR_0_DS_3");
   
  PR_DS_0->enable(TIME_STEP);
  PR_DS_1->enable(TIME_STEP);
  PR_DS_2->enable(TIME_STEP);
  PR_DS_3->enable(TIME_STEP);
   
  Field *Pickup_node_trans_field = Pickup_node->getField("translation");
  Field *Pickup_node_target_field = Pickup_node->getField("target");
  Field *Pickup_node_emergency_field = Pickup_node->getField("emergency");
  
  Field *PR_LED_0_lBLStrength_field = PR_LED_0->getField("IBLStrength");
  Field *PR_LED_1_lBLStrength_field = PR_LED_1->getField("IBLStrength");
  Field *PR_LED_2_lBLStrength_field = PR_LED_2->getField("IBLStrength");
  Field *PR_LED_3_lBLStrength_field = PR_LED_3->getField("IBLStrength");
  
  Field *PR_LED_0_trans_field = PR_LED_0->getField("translation");
  Field *PR_LED_1_trans_field = PR_LED_1->getField("translation");
  Field *PR_LED_2_trans_field = PR_LED_2->getField("translation");
  Field *PR_LED_3_trans_field = PR_LED_3->getField("translation");
  
  Field *direction_lamps_field = Pickup_node->getField("direction_lamps");
  Field *sensors_field = Pickup_node->getField("sensors");
  
  PR_LED_0_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
  PR_LED_1_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
  PR_LED_2_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
  PR_LED_3_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
  
  int duration = (1000/ TIME_STEP) * TIME_STEP;
  
  const double *pos_default = Pickup_node->getPosition();
  double pos[3] = {0,0,0};
  double pos_LEDS[3] = {0,0,0};

  pos[0] = pos_default[0];
  pos[1] = pos_default[1];
  pos[2] = pos_default[2];
  
  
  int posX = round(10 * pos[0]);
  int posY = round(10 * pos[1]);
  
  
  const double *targetVec = Pickup_node_target_field->getSFVec2f();
  int tarX = int(targetVec [0]);
  int tarY = int(targetVec[1]);
  
  bool emergency_status = false;
  
  while (supervisor->step(duration) != -1) {
    targetVec = Pickup_node_target_field->getSFVec2f();
    tarX = int(targetVec [0]);
    tarY = int(targetVec[1]);
    
    emergency_status = Pickup_node_emergency_field->getSFBool();
    
    if(emergency_status || ( tarX == posX && tarY == posY)){
      PR_LED_1_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_2_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_3_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_0_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      direction_lamps_field->setSFString("off");
    }  
    else if(tarX > posX){
      pos[0] = pos[0] + 0.1;
      PR_LED_0_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_1_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_2_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_3_lBLStrength_field->setSFFloat(lBL_Strength_ON);
      direction_lamps_field->setSFString("forward");

    }
    else if(tarX < posX){
      pos[0] = pos[0] - 0.1;
      PR_LED_0_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_2_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_3_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_1_lBLStrength_field->setSFFloat(lBL_Strength_ON);
      direction_lamps_field->setSFString("backwards");
    }
    else if(tarY > posY){
      pos[1] = pos[1] + 0.1;
      PR_LED_0_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_1_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_3_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_2_lBLStrength_field->setSFFloat(lBL_Strength_ON);
      direction_lamps_field->setSFString("left");
    }
    else if(tarY < posY){
      pos[1] = pos[1] - 0.1;
      PR_LED_1_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_2_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_3_lBLStrength_field->setSFFloat(lBL_Strength_OFF);
      PR_LED_0_lBLStrength_field->setSFFloat(lBL_Strength_ON);
      direction_lamps_field->setSFString("right");
    }
 
  
    Pickup_node_trans_field->setSFVec3f(pos);
    
    pos_LEDS[0] = pos[0];
    pos_LEDS[1] = pos[1] -0.04;
    pos_LEDS[2] = pos[2] + 0.05;
    PR_LED_0_trans_field->setSFVec3f(pos_LEDS);
    
    pos_LEDS[0] = pos[0] -0.04;
    pos_LEDS[1] = pos[1];
    pos_LEDS[2] = pos[2] + 0.05;
    PR_LED_1_trans_field->setSFVec3f(pos_LEDS);
    
    pos_LEDS[0] = pos[0];
    pos_LEDS[1] = pos[1] + 0.04;
    pos_LEDS[2] = pos[2] + 0.05;
    PR_LED_2_trans_field->setSFVec3f(pos_LEDS);
    
    pos_LEDS[0] = pos[0] + 0.04;
    pos_LEDS[1] = pos[1];
    pos_LEDS[2] = pos[2] + 0.05;
    PR_LED_3_trans_field->setSFVec3f(pos_LEDS);
    
    posX = round(10 * pos[0]);
    posY = round(10 * pos[1]);
    

    sensors_field->setMFInt32(0,PR_DS_0->getValue());
    sensors_field->setMFInt32(1,PR_DS_1->getValue());
    sensors_field->setMFInt32(2,PR_DS_2->getValue());
    sensors_field->setMFInt32(3,PR_DS_3->getValue());
    
    // std::cout << "x = " << round(10 *pos [0]) << " y = " << round(10* pos [1])<< " z = "  << round(10* pos [2]) << std::endl;
    // std::cout << "PR_DS_0 = " << PR_DS_0->getValue() << std::endl;
    // std::cout << "PR_DS_1 = " << PR_DS_1->getValue() << std::endl;
    // std::cout << "PR_DS_2 = " << PR_DS_2->getValue() << std::endl;
    // std::cout << "PR_DS_3 = " << PR_DS_3->getValue() << std::endl;
  };


  delete supervisor;
  return 0;
}
