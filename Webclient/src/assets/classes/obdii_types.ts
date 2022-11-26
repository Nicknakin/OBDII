
export enum OBDIIResponseType {
  OBDIIResponseTypeBitfield = 0,
  OBDIIResponseTypeNumeric = 1,
  OBDIIResponseTypeString = 2,
  OBDIIResponseTypeOther = 3,
}

export class OBDIICommand {
  name: String;
  payload: Number;
  responseType: Number;
  expectedResponseLength: Number;
}

export class OBDIITroubleCodes {
  public troubleCodes: String;
  public numTroubleCodes: Number;
}

export class OBDIIOxygenSensorVoltageOrCurrent{
  public voltage: Number;
  public current: Number;
}

export class OBDIIOxygenSensorTrimOrRatio{
  public shortTermFuelTrim: Number;
  public fuelAirEquivalenceRatio: Number;
}

export class OBDIIOxygenSensorValues{
  public voltageOrCurrent: OBDIIOxygenSensorVoltageOrCurrent;
  public trimOrRatio: OBDIIOxygenSensorTrimOrRatio;
}

export class OBDIIResponseValue{
  numericValue: Number;
  bitfieldValue: Number;
  stringValue: String;
  DTCs: OBDIITroubleCodes;
  oxygenSensorValues: OBDIIOxygenSensorValues;
}

export class OBDIIResponse{
  success: Number;
  command: OBDIICommand;
  value: OBDIIResponseValue;
}
