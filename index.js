const express = require("express");
const expressLayouts = require("express-ejs-layouts");
const app = express();

const PORT = process.env.PORT || 80;

app.use(expressLayouts);
app.set("view engine", "ejs");

app.get("/", (_, res) => {
  res.render("pages/home");
});

app.get("/visualizations/:pagename", (req, res) => {
  res.render(`pages/${req.params.pagename}`);
});

app.use(express.static(__dirname + "/public"));
app.listen(PORT, () => {
  console.log(`O site está servido em http://localhost:${PORT}`)
});