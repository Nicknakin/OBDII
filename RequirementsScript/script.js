const csv = require('csv-parse');
const fs = require('fs');;

const fileName = process.argv[process.argv.length-1];


const format = (row) => `\\subsection{${row[0]}}
\\subsubsection{Description}
${row[1]}
\\subsubsection{Source}
${row[2]}
\\subsubsection{Constraints}
${row[3]}
\\subsubsection{Standards}
${row[4]}
\\subsubsection{Priority}
${row[5]}
`;

fs.readFile(fileName, 'utf8', (err, data) => {
    console.log(data.split('\n').map(row => row.split(',')).map(format).join('\n\n'));
});
