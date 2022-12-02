import { readFile } from 'fs/promises';
import { spawn } from 'child_process'
import express from 'express'
import bodyParser from 'body-parser';
const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

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

app.get("/full-dump", (req, res) => {
  const requestTime = Date.now()
  //Spawn program
  const pyProgram = spawn(runner, ["-r"], { shell: true });
  //On program exit handler
  pyProgram.on('exit', async (code, signal) => {
    let data;
    if (code == 0 | true) {
      data = JSON.parse(
        await readFile(
          new URL('./export_data.json', import.meta.url)
        )
      );
    }

    //Construct response object
    const response = {
      code,
      signal,
      diagnostics: data,
    };

    //Log request and respond
    res.end(JSON.stringify(response));
    logHistory({ endpoint: "/full-dump", requestTime, responseTime: new Date(), response });
  }).stdout.on('data', (data) => { // On output handler
    console.log(data.toString());
  })
});


app.get("/clear-dtc", (_, res) => {
  const requestTime = Date.now()
  const pyProgram = spawn(runner, ["-c"], { shell: true });
  pyProgram.on('exit', (code, signal) => {
    const response = {
      code,
      signal,
    };

    //Log request and respond
    res.end(JSON.stringify(response));
    logHistory({ endpoint: "/clear-dtc", requestTime, responseTime: new Date(), response });
  });
});

//Endpoint to run a manual query
app.post("/manual-query", (req, res) => {
  const requestTime = Date.now()
  const { service, pid } = req?.body;
  console.log(`-s ${service} ${pid}`);
  const pyProgram = spawn(runner, [`-s ${service} ${pid}`], { shell: true });
  pyProgram.on('exit', async (code, signal) => {
    let data;
    if (code == 0 || true) {
      data = JSON.parse(
        await readFile(
          new URL('./specific_export.json', import.meta.url)
        )
      );
    }

    //Construct response object
    const response = {
      code,
      signal,
      diagnostics: data,
    };

    //Log request and respond
    res.end(JSON.stringify(response));
    logHistory({ endpoint: "/manual-query", requestTime, responseTime: new Date(), response });
  }).stdout.on('data', (data) => { // On output handler
    console.log(data.toString());
  })
});

app.post("/history", async (req, res) => {
  let response = await getHistory(req?.body ?? {});
  res.end(JSON.stringify(response));
});

//Endpoint that gets the supported PIDS from the python program
app.get("/supported-pids", async (_req, res) => {
  const requestTime = Date.now()

  let response = await getSupportedPids();

  // Log request and respond TODO Put inside of program exit handler
  logHistory({ endpoint: "/supported-pids", requestTime, responseTime: new Date(), response });
  res.end(JSON.stringify(response));
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
      ORDER BY requestTime DESC
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

async function getSupportedPids() {
  return pool.getConnection()
    .then(async conn => {
      return conn.query(`
      SELECT \`Mode (hex)\` service, \`PID (hex)\` pid, p.Description
      FROM PIDS p
      INNER JOIN ActivePIDS ap on p.Description=ap.Description;`)
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
}
