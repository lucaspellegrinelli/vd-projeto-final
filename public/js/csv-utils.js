function readCSV(path) {
  const csvContent = $.ajax({type: "GET", url: path, async: false}).responseText;
  const csvLines = csvContent.split(/\r?\n/);
  const csvCells = csvLines.map(line => line.split(/\s*,\s*/));
  const columnNames = {};

  csvCells[0].forEach(name => columnNames[name] = []);
  Object.keys(columnNames).forEach((key, key_i) => {
    for (let i = 1; i < csvLines.length; i++) {
      columnNames[key].push(parseFloat(csvCells[i][key_i]));
    }
  });

  return columnNames;
}