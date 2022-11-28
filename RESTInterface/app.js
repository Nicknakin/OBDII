import { readFile } from 'fs/promises';
import { spawn } from 'child_process'
import express from 'express'
const app = express();

import mariadb from 'mariadb';
import config from './config.json' assert { type: 'json' };

const pool = mariadb.createPool({
  host: config.db.host,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
  connectionLimit: 5,
});

//Get the runner and program from command line arguments or use defaults
const runner = process.argv.length > 4 ? process.argv[process.argv.length - 2] : "python3 ../OBDIIInterface/OBD.py";

//Prepare an express server on port 8081
const server = app.listen(8081, function() {
  var host = server.address().address;
  var port = server.address().port;
  console.log("OBDII - REST Server listening at http://%s:%s", host, port);
})

//TODO Endpoint to get all info from the car
app.get("/full-dump", (req, res) => {
  const requestTime = Date.now()
  //Spawn program
  const pyProgram = spawn(runner, ["-r"], { shell: true });
  //Prepare output string
  let str = "";

  //On program exit handler
  pyProgram.on('exit', async (code, signal) => {
    let data = JSON.parse(
      await readFile(
        new URL('./export_data.json', import.meta.url)
      )
    );;
    //Construct response object
    const response = {
      code,
      signal,
      diagnostics: data,
      //diagnostics: JSON.parse(str),
    };

    //Log request and respond
    logHistory({ endpoint: "/full-dump", requestTime, responseTime: new Date(), response });
    res.end(JSON.stringify(response));
  }).stdout.on('data', (data) => { // On output handler
    str += data.toString();
    consol.log(data.toString());
  })
});

//TODO Endpoint to run a manual query
app.get("/manual-query", (req, res) => {
  const requestTime = Date.now()
  //Spawn program
  const pyProgram = spawn(runner, [program]);
  //Prepare output string
  let str = "";

  //On program exit handler
  pyProgram.on('exit', (code, signal) => {
    //Construct response object
    const response = {
      code,
      signal,
      diagnostics: [],//JSON.parse(str),
    };

    //Log request and respond
    logHistory({ endpoint: "/manual-query", requestTime, responseTime: new Date(), response });
    res.end(JSON.stringify(response));
  }).stdout.on('data', (data) => { // On output handler
    str += data.toString();
  })
});

//TODO Endpoint to get history of requests
//TODO Default last ~100 entries, expect req.body.count to hold requested count of entries (max 1000)
//TODO Default start from most recent, expect req.body.start to hold the requested start index (skip n many entries)
app.get("/history", async (_req, res) => {
  const requestTime = Date.now()
  //TODO Get history of all requests
  let response = await getHistory({});
  // Log request and respond
  logHistory({ endpoint: "/history", requestTime, responseTime: new Date(), });
  res.end(JSON.stringify(response));
});

//TODO Endpoint that gets the supported PIDS from the python program
app.get("/supported-pids", (_req, res) => {
  const requestTime = Date.now()
  //TODO Start python program with arguments to get supported pids

  //TODO Prepare output string

  //TODO Define handlers for python program

  // Log request and respond TODO Put inside of program exit handler
  logHistory({ endpoint: "/history", requestTime, responseTime: new Date(), response });
  res.end(/*TODO Data goes here*/);
});

function logHistory(data) {
  data.requestTime = new Date(data.requestTime).toISOString().slice(0, 19).replace('T', ' ');
  data.responseTime = new Date(data.responseTime).toISOString().slice(0, 19).replace('T', ' ');
  pool.getConnection()
    .then(conn => {
      conn.query(`
      INSERT INTO History (endpoint, response, requestTime, responseTime)
      VALUES (?, ?, ?, ?);`, [data.endpoint, JSON.stringify(data.response) ?? null, data.requestTime, data.responseTime])
        .then(res => {
          console.log(res);
          conn.end();
        })
        .catch(err => {
          console.error(err);
          conn.end();
        });
    });
};

async function getHistory(data) {
  data.count = data?.count ?? 100;
  data.count = (data.count < 1000) ? data.count : 1000;
  data.start = data?.start ?? 0;
  return pool.getConnection()
    .then(async conn => {
      return conn.query(`
      SELECT endpoint, response, requestTime, responseTime 
      FROM History h
      WHERE h.id>=${data.start}
      LIMIT ${data.count};`)
        .then(rows => {
          conn.end();
          return { Success: true, rows };
        })
        .catch(err => {
          console.error(err);
          conn.end();
          return { Success: false, err };
        });
    });
};
