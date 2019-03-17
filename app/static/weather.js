function weather() {
    var chart = new AmCharts.AmSerialChart();
    chart.dataProvider = lineChartData;
    chart.pathToImages = "static/";
    chart.categoryField = "date";
    chart.marginTop = 40;
    //chart.addTitle(num_hours.toString() + ' hour forecast for ' + location);

    // AXES
    // category                
    var categoryAxis = chart.categoryAxis;
    categoryAxis.parseDates = true; 
    categoryAxis.minPeriod = "3hh";
    categoryAxis.equalSpacing = true;
    categoryAxis.dashLength = 4;
    categoryAxis.gridAlpha = .15;
    categoryAxis.dateFormats = [{period: "DD", format: "EEE M/D"}, {period: "hh", format: "LA"}];

    // temperature value axis
    var tempAxis = new AmCharts.ValueAxis();
    tempAxis.dashLength = 4;
    tempAxis.gridAlpha = 0;
    tempAxis.unit = ' ' + units;
    chart.addValueAxis(tempAxis);

    // pop value axis
    var popAxis = new AmCharts.ValueAxis();
    popAxis.position = "right";
    popAxis.dashLength = 4;
    popAxis.gridAlpha = 0;
    popAxis.minimum = 0;
    popAxis.maximum = 10;
    popAxis.unit = "mm";
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
    feel.valueField = (units == 'F') ? "feel" : "feel_c";
    feel.title = "Feels like";
    feel.lineColor = 'green';
    feel.balloonText = "[[value]] " + units;
    chart.addGraph(feel);

    // temp graph
    var temp = new AmCharts.AmGraph();
    temp.valueAxis = tempAxis;
    temp.type = "smoothedLine";
    temp.valueField = (units == 'F') ? "temp" : "temp_c";
    temp.title = "Temperature";
    temp.lineColor = 'red';
    temp.balloonText = "[[value]] " + units;
    chart.addGraph(temp);

    // pop graph
    var pop = new AmCharts.AmGraph();
    pop.valueAxis = popAxis;
    pop.type = "smoothedLine";
    pop.valueField = "pop";
    pop.title = "mm of precipitation";
    pop.lineColor = 'blue';
    pop.balloonText = "[[value]] mm";
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
