function weather() {
    var chart = new AmCharts.AmSerialChart();
    chart.dataProvider = lineChartData;
    chart.pathToImages = "static/";
    chart.categoryField = "date";
    chart.marginTop = 40;
    chart.addTitle(num_hours.toString() + ' hour forecast for ' + city);

    // AXES
    // category                
    var categoryAxis = chart.categoryAxis;
    categoryAxis.parseDates = true; 
    categoryAxis.minPeriod = "hh"; 
    categoryAxis.dashLength = 4;
    categoryAxis.gridAlpha = .15;
    categoryAxis.dateFormats = [{period: "DD", format: "EEE M/D"}, {period: "hh", format: "LA"}]

    // temperature value axis
    var tempAxis = new AmCharts.ValueAxis();
    tempAxis.dashLength = 4;
    tempAxis.gridAlpha = 0;
    tempAxis.unit = " F";
    chart.addValueAxis(tempAxis);

    // pop value axis
    var popAxis = new AmCharts.ValueAxis();
    popAxis.position = "right";
    popAxis.dashLength = 4;
    popAxis.gridAlpha = 0;
    popAxis.minimum = 0;
    popAxis.maximum = 100;
    popAxis.unit = "%";
    chart.addValueAxis(popAxis);

    // GRAPH
    // icons graph
    var icons = new AmCharts.AmGraph();
    icons.position = "right";
    icons.type = "line";
    icons.valueAxis = popAxis;
    icons.valueField = "icon_pos";
    icons.bulletSize = 21; 
    icons.customBulletField = "icon"; 
    icons.lineThickness = 0;
    icons.visibleInLegend = false;
    icons.showBalloon = false;
    chart.addGraph(icons);

    // feels like graph
    var feel = new AmCharts.AmGraph();
    feel.valueAxis = tempAxis;
    feel.type = "smoothedLine";
    feel.valueField = "feel";
    feel.title = "Feels like";
    feel.lineColor = 'green';
    feel.balloonText = "[[value]] F";
    chart.addGraph(feel);

    // temp graph
    var temp = new AmCharts.AmGraph();
    temp.valueAxis = tempAxis;
    temp.type = "smoothedLine";
    temp.valueField = "temp";
    temp.title = "Temperature";
    temp.lineColor = 'red';
    temp.balloonText = "[[value]] F";
    chart.addGraph(temp);

    // pop graph
    var pop = new AmCharts.AmGraph();
    pop.valueAxis = popAxis;
    pop.type = "smoothedLine";
    pop.valueField = "pop";
    pop.title = "% chance of rain";
    pop.lineColor = 'blue';
    pop.balloonText = "[[value]]%";
    chart.addGraph(pop);

    // CURSOR
    var chartCursor = new AmCharts.ChartCursor();
    chartCursor.categoryBalloonDateFormat = "M/D LA";
    chartCursor.cursorColor = "orange";
    chart.addChartCursor(chartCursor);

    // LEGEND
    var legend = new AmCharts.AmLegend();
    legend.position = "bottom";
    chart.addLegend(legend);

    // WRITE
    chart.write("chart_div");
};
