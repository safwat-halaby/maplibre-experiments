const express = require('express');
if (!process.argv[2]) {
    console.error('Usage: node run.js <PORT>')
    return -1;
}
const PORT = parseInt(process.argv[2]);
const app = express();
app.use(express.static('.'));
app.get('/', (req, res) => {
  res.send('Hello World!')
})
app.listen(PORT, () => {
    console.log(`Listening on port ${PORT}`);
});