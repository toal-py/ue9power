window.onload = function() {
    var dropdowns = JSON.parse(document.getElementById("dropdowns").getAttribute("data-dropdowns"))
    var yearSel1 = document.getElementById("year1");
    var monthSel1 = document.getElementById("month1");
    var yearSel2 = document.getElementById("year2");
    var monthSel2 = document.getElementById("month2");
    for (var x in dropdowns) {
      yearSel1.options[yearSel1.options.length] = new Option(x, x);
    }
    for (var x in dropdowns) {
      yearSel2.options[yearSel2.options.length] = new Option(x, x);
    }

    yearSel1.onchange = function() {
      monthSel1.length = 1;
      var z1 = dropdowns[yearSel1.value];
      for (var i = 0; i < z1.length; i++) {
      if (z1[i] != monthSel2.value || yearSel1.value != yearSel2.value){ 
      monthSel1.options[monthSel1.options.length] = new Option(z1[i], z1[i]);
      }
    }}

    yearSel2.onchange = function() {
      monthSel2.length = 1;
      var z2 = dropdowns[yearSel2.value];
      for (var i = 0; i < z2.length; i++) {
      if (z2[i] != monthSel1.value || yearSel1.value != yearSel2.value){
      monthSel2.options[monthSel2.options.length] = new Option(z2[i], z2[i]);
      }
    }}

    monthSel1.onchange = function() {
      if (dropdowns[yearSel2.value] && monthSel2.value == ""){
      monthSel2.length = 1;
      var z2 = dropdowns[yearSel2.value];
      for (var i = 0; i < z2.length; i++) {
      if (z2[i] != monthSel1.value || yearSel1.value != yearSel2.value){
      monthSel2.options[monthSel2.options.length] = new Option(z2[i], z2[i]);
      }
    }}
    else if (monthSel1.value == monthSel2.value && yearSel1.value == yearSel2.value) {
      monthSel2.length = 1;
      var z2 = dropdowns[yearSel2.value];
      for (var i = 0; i < z2.length; i++) {
      if (z2[i] != monthSel1.value || yearSel1.value != yearSel2.value){
      monthSel2.options[monthSel2.options.length] = new Option(z2[i], z2[i]);
    }
    }}}

    monthSel2.onchange = function() {
      if (dropdowns[yearSel1.value] && monthSel1.value == ""){
      monthSel1.length = 1;
      var z1 = dropdowns[yearSel1.value];
      for (var i = 0; i < z1.length; i++) {
      if (z1[i] != monthSel2.value || yearSel1.value != yearSel2.value){
      monthSel1.options[monthSel1.options.length] = new Option(z1[i], z1[i]);
      }
    }}
    else if (monthSel1.value == monthSel2.value && yearSel1.value == yearSel2.value){
      monthSel1.length = 1;
      var z1 = dropdowns[yearSel1.value];
      for (var i = 0; i < z1.length; i++) {
      if (z1[i] != monthSel2.value || yearSel1.value != yearSel2.value){
      monthSel1.options[monthSel1.options.length] = new Option(z1[i], z1[i]);
      }
    }
    }
  }
}