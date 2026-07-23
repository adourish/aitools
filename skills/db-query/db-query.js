#!/usr/bin/env node
// Skill: db-query
// Usage: node db-query.js "<SQL>"
// Reads credentials from automation KeePass: Database/SERIO Oracle DB (oasis_er) Dev-Test

const { execFileSync } = require('child_process');
const fs = require('fs');
const oracledb = require('oracledb');

// KeePass DB auto-discovery: env var > C:\keys (FDA laptop / Shared-AI-Service) > G:\My Drive (REI laptop)
const KDB  = process.env.KEEPASS_DB  ||
  (fs.existsSync('C:\\keys\\automation-keys.kdbx')
    ? 'C:\\keys\\automation-keys.kdbx'
    : 'G:\\My Drive\\Areas\\Keys\\automation-keys.kdbx');
const KKEY = process.env.KEEPASS_KEY ||
  (fs.existsSync('C:\\keys\\automation-keys.keyfile')
    ? 'C:\\keys\\automation-keys.keyfile'
    : 'C:\\Users\\adourish\\.keepass\\automation-keys.keyfile');

const ENTRY = 'Database/SERIO Oracle DB (oasis_er) Dev-Test';

function kpGet(field) {
  return execFileSync('keepassxc-cli', [
    'show', '--key-file', KKEY, '--no-password', '--show-protected',
    '--attributes', field, KDB, ENTRY
  ], { encoding: 'utf8' }).trim();
}

async function runQuery(sql, binds = []) {
  const user          = kpGet('UserName');
  const password      = kpGet('Password');
  const connectString = kpGet('URL');
  let conn;
  try {
    conn = await oracledb.getConnection({ user, password, connectString });
    const result = await conn.execute(sql, binds, { outFormat: oracledb.OUT_FORMAT_OBJECT });
    return result.rows;
  } finally {
    if (conn) await conn.close();
  }
}

if (require.main === module) {
  const sql = process.argv[2];
  if (!sql) {
    console.error('Usage: node db-query.js "<SQL>"');
    process.exit(1);
  }
  runQuery(sql)
    .then(rows => console.log(JSON.stringify(rows, null, 2)))
    .catch(err => { console.error(err.message); process.exit(1); });
}

module.exports = { runQuery };