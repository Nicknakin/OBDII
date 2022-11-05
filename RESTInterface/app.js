import { spawn } from 'child_process'
import express from 'express'
const app = express();

const runner = process.argv.length > 4 ? process.argv[process.argv.length - 2] : "python";
const program = process.argv.length > 4 ? process.argv[process.argv.length - 1] : "main.py";

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
      diagnostics: [["name", "thing"], ["name2", "thing2"]]//str
    };
    console.log(response);
    res.end(JSON.stringify(response));
  }).stdout.on('data', (data) => {
    str += data.toString();
  })
});
