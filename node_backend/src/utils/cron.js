const cron = require('node-cron');
const { exec } = require('child_process');
const archiver = require('archiver');
const fs = require('fs');
const nodemailer = require('nodemailer');
const path = require('path');

module.exports = (app) => {
  cron.schedule('59 23 * * *', async () => {
    const date = new Date().toISOString().slice(0, 10);
    const backupDir = path.join(__dirname, '../../backup');
    if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir);

    // Export PostgreSQL
    const pgFile = `${backupDir}/pg-${date}.sql`;
    await new Promise((resolve, reject) => {
      exec(`pg_dump ${process.env.PG_URI} > ${pgFile}`, (err) => err ? reject(err) : resolve());
    });

    // Export MongoDB
    const mongoDir = `${backupDir}/mongo-${date}`;
    await new Promise((resolve, reject) => {
      exec(`mongodump --uri="${process.env.MONGO_URI}" --out=${mongoDir}`, (err) => err ? reject(err) : resolve());
    });

    // Zip both
    const zipPath = `${backupDir}/${date}-backup.zip`;
    const output = fs.createWriteStream(zipPath);
    const archive = archiver('zip');
    archive.pipe(output);
    archive.file(pgFile, { name: `pg-${date}.sql` });
    archive.directory(mongoDir, `mongo-${date}`);
    await archive.finalize();

    // Email
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
      }
    });
    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: process.env.EMAIL_TO,
      subject: `Daily DB Backup - ${date}`,
      text: 'See attached backup.',
      attachments: [{ filename: `${date}-backup.zip`, path: zipPath }]
    });

    // Cleanup
    fs.unlinkSync(pgFile);
    fs.rmSync(mongoDir, { recursive: true, force: true });
  });
};