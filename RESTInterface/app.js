import { spawn } from 'child_process'
import express from 'express'
const app = express();

const runner = process.argv.length > 4 ? process.argv[process.argv.length - 2] : "python";
const program = process.argv.length > 4 ? process.argv[process.argv.length - 1] : "../OBDIIInterface/OBD.py";

const server = app.listen(8081, function() {
  var host = server.address().address;
  var port = server.address().port;
  console.log("OBDII - REST Server listening at http://%s:%s", host, port);
})

app.get("/full-dump", (_req, res) => {
  const pyProgram = spawn(runner, [program]);
  let str = "";
  pyProgram.on('exit', (code, signal) => {
    const response = {
      code,
      signal,
      diagnostics: [
        {name: 'mode1SupportedPIDs_1_to_20', value: "Temporary Value for testing purposes"},
        {name: 'monitorStatus', value: "Temporary Value for testing purposes"},
        {name: 'freezeDTC', value: "Temporary Value for testing purposes"},
        {name: 'fuelSystemStatus', value: "Temporary Value for testing purposes"},
        {name: 'calculatedEngineLoad', value: "Temporary Value for testing purposes"},
        {name: 'engineCoolantTemperature', value: "Temporary Value for testing purposes"},
        {name: 'bank1ShortTermFuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'bank1LongTermFueldTrim', value: "Temporary Value for testing purposes"},
        {name: 'bank2ShortTermFuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'bank2LongTermFuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'fuelPressure', value: "Temporary Value for testing purposes"},
        {name: 'intakeManifoldAbsolutePressure', value: "Temporary Value for testing purposes"},
        {name: 'engineRPMs', value: "Temporary Value for testing purposes"},
        {name: 'vehicleSpeed', value: "Temporary Value for testing purposes"},
        {name: 'timingAdvance', value: "Temporary Value for testing purposes"},
        {name: 'intakeAirTemperature', value: "Temporary Value for testing purposes"},
        {name: 'mafAirFlowRate', value: "Temporary Value for testing purposes"},
        {name: 'throttlePosition', value: "Temporary Value for testing purposes"},
        {name: 'commandedSecondaryAirStatus', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensorsPresentIn2Banks', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor1_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor2_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor3_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor4_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor5_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor6_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor7_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor8_fuelTrim', value: "Temporary Value for testing purposes"},
        {name: 'conformingStandards', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensorsPresentIn4Banks', value: "Temporary Value for testing purposes"},
        {name: 'auxiliaryInputStatus', value: "Temporary Value for testing purposes"},
        {name: 'runtimeSinceEngineStart', value: "Temporary Value for testing purposes"},
        {name: 'mode1SupportedPIDs_21_to_40', value: "Temporary Value for testing purposes"},
        {name: 'distanceTraveledWithMalfunctionIndicatorLampOn', value: "Temporary Value for testing purposes"},
        {name: 'fuelRailPressure', value: "Temporary Value for testing purposes"},
        {name: 'fuelRailGaugePressure', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor1_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor2_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor3_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor4_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor5_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor6_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor7_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor8_fuelAirRatioVoltage', value: "Temporary Value for testing purposes"},
        {name: 'commandedEGR', value: "Temporary Value for testing purposes"},
        {name: 'egrError', value: "Temporary Value for testing purposes"},
        {name: 'commandedEvaporativePurge', value: "Temporary Value for testing purposes"},
        {name: 'fuelTankLevelInput', value: "Temporary Value for testing purposes"},
        {name: 'warmUpsSinceCodesCleared', value: "Temporary Value for testing purposes"},
        {name: 'distanceTraveledSinceCodesCleared', value: "Temporary Value for testing purposes"},
        {name: 'evaporativeSystemVaporPressure', value: "Temporary Value for testing purposes"},
        {name: 'absoluteBarometricPressure', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor1_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor2_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor3_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor4_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor5_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor6_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor7_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'oxygenSensor8_fuelAirRatioCurrent', value: "Temporary Value for testing purposes"},
        {name: 'catalystTemperatureBank1Sensor1', value: "Temporary Value for testing purposes"},
        {name: 'catalystTemperatureBank2Sensor1', value: "Temporary Value for testing purposes"},
        {name: 'catalystTemperatureBank1Sensor2', value: "Temporary Value for testing purposes"},
        {name: 'catalystTemperatureBank2Sensor2', value: "Temporary Value for testing purposes"},
        {name: 'mode1SupportedPIDs_41_to_60', value: "Temporary Value for testing purposes"},
        {name: 'currentDriveCycleMonitorStatus', value: "Temporary Value for testing purposes"},
        {name: 'controlModuleVoltage', value: "Temporary Value for testing purposes"},
        {name: 'absoluteLoadValue', value: "Temporary Value for testing purposes"},
        {name: 'fuelAirCommandEquivalenceRatio', value: "Temporary Value for testing purposes"},
        {name: 'relativeThrottlePosition', value: "Temporary Value for testing purposes"},
        {name: 'ambientAirTemperature', value: "Temporary Value for testing purposes"},
        {name: 'absoluteThrottlePositionB', value: "Temporary Value for testing purposes"},
        {name: 'absoluteThrottlePositionC', value: "Temporary Value for testing purposes"},
        {name: 'acceleratorPedalPositionD', value: "Temporary Value for testing purposes"},
        {name: 'acceleratorPedalPositionE', value: "Temporary Value for testing purposes"},
        {name: 'acceleratorPedalPositionF', value: "Temporary Value for testing purposes"},
        {name: 'commandedThrottleActuator', value: "Temporary Value for testing purposes"},
        {name: 'timeRunWithMalfunctionIndicatorLampOn', value: "Temporary Value for testing purposes"},
        {name: 'timeSinceTroubleCodesCleared', value: "Temporary Value for testing purposes"},
        {name: 'DTCs', value: "Temporary Value for testing purposes"},
        {name: 'mode9SupportedPIDs', value: "Temporary Value for testing purposes"},
        {name: 'vinMessageCount', value: "Temporary Value for testing purposes"},
        {name: 'VIN', value: "Temporary Value for testing purposes"},
        {name: 'ECUName', value: "Temporary Value for testing purposes"}
      ]
      // diagnostics: JSON.parse(str),
    };
    res.end(JSON.stringify(response));
  }).stdout.on('data', (data) => {
    str += data.toString();
  })
});
