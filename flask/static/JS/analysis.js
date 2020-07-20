function grapher() {
  let df = document.getElementById("dataframe").value
  df = JSON.parse(df)

  /* -----------------Define Lists for Slider Variables-----------------------*/
  var xranges = [];
  var thresholds = [];
  var polynomials = [];
  var windows = [];
  var buffers = [];
  var minDistances = [];
  /* -----------------------------------------------------------------------------------*/

  for (var i = 0; i < df.length; i++) {
    var istring = i.toString()
    df[i] = JSON.parse(df[i])

    /* --------------Define Data Start-----------------------------------------------*/
    var trace1 = {
      x: Object.values(df[i].time),
      y: Object.values(df[i].disp),
      type: 'scatter'
    };
    var trace2 = {
      x: [1, 2, 3],
      y: [1, 2, 3],
      type: 'scatter'
    };
    var trace3 = {
      x: [1, 2, 3],
      y: [9, 9, 9],
      type: 'scatter'
    };
    var data = [trace2, trace3];
    /* ------------------------------------------------------------------------------------*/

    /* ---------------Define Sliders Start------------------------------------------------*/
    var threshSlider = {
      len: .5,
      pad: {t: 100},
      currentvalue: {
       xanchor: 'right',
       prefix: 'Thresh: ',
       font: {
         color: '#888',
         size: 10
       }
     },
      steps: [{
        label: '0',
        method: 'restyle',
        args: ['thresh', '0']
      }, {
        label: '.1',
        method: 'restyle',
        args: ['thresh', '.1']
      }, {
        label: '.2',
        method: 'restyle',
        args: ['thresh', '.2']
      }, {
        label: '.3',
        method: 'restyle',
        args: ['thresh', '.3']
      }, {
        label: '.4',
        method: 'restyle',
        args: ['thresh', '.4']
      }, {
        label: '.5',
        method: 'restyle',
        args: ['thresh', '.5']
      }, {
        label: '.6',
        method: 'restyle',
        args: ['thresh', '.6']
      }, {
        label: '.7',
        method: 'restyle',
        args: ['thresh', '.7']
      }, {
        label: '.8',
        method: 'restyle',
        args: ['thresh', '.8']
      }, {
        label: '.9',
        method: 'restyle',
        args: ['thresh', '.9']
      }, {
        label: '1',
        method: 'restyle',
        args: ['thresh', '1']
      }]
    }
    var buffSlider = {
      len: .5,
      pad: {t: 160},
      currentvalue: {
       xanchor: 'right',
       prefix: 'Buff: ',
       font: {
         color: '#888',
         size: 10
       }
     },
      steps: [{
        label: '0',
        method: 'restyle',
        args: ['buff', '0']
      }, {
        label: '1',
        method: 'restyle',
        args: ['buff', '1']
      },{
        label: '2',
        method: 'restyle',
        args: ['buff', '2']
      },{
        label: '3',
        method: 'restyle',
        args: ['buff', '3']
      }, {
        label: '4',
        method: 'restyle',
        args: ['buff', '4']
      }, {
        label: '5',
        method: 'restyle',
        args: ['buff', '5']
      }, {
        label: '6',
        method: 'restyle',
        args: ['buff', '6']
      }, {
        label: '7',
        method: 'restyle',
        args: ['buff', '7']
      }, {
        label: '8',
        method: 'restyle',
        args: ['buff', '8']
      }, {
        label: '9',
        method: 'restyle',
        args: ['buff', '9']
      }, {
        label: '10',
        method: 'restyle',
        args: ['buff', '10']
      }]
    }
    var minDistSlider = {
      len: .5,
      x: .5,
      pad: {t:100},
      currentvalue: {
       xanchor: 'right',
       prefix: 'minDist: ',
       font: {
         color: '#888',
         size: 10
       }
     },
      steps: [{
        label: '0',
        method: 'restyle',
        args: ['mdist', '0']
      }, {
        label: '1',
        method: 'restyle',
        args: ['mdist', '1']
      },{
        label: '2',
        method: 'restyle',
        args: ['mdist', '2']
      },{
        label: '3',
        method: 'restyle',
        args: ['mdist', '3']
      }, {
        label: '4',
        method: 'restyle',
        args: ['mdist', '4']
      }, {
        label: '5',
        method: 'restyle',
        args: ['mdist', '5']
      }, {
        label: '6',
        method: 'restyle',
        args: ['mdist', '6']
      }, {
        label: '7',
        method: 'restyle',
        args: ['buff', '7']
      }, {
        label: '8',
        method: 'restyle',
        args: ['mdist', '8']
      }, {
        label: '9',
        method: 'restyle',
        args: ['mdist', '9']
      }, {
        label: '10',
        method: 'restyle',
        args: ['mdist', '10']
      }]
    }
    var polySlider = {
      len: .5,
      pad: {t: 220},
      currentvalue: {
       xanchor: 'right',
       prefix: 'Poly: ',
       font: {
         color: '#888',
         size: 10
       }
     },
      steps: [{
        label: '3',
        method: 'restyle',
        args: ['polynom', '3']
      }, {
        label: '4',
        method: 'restyle',
        args: ['polynom', '4']
      }, {
        label: '5',
        method: 'restyle',
        args: ['polynom', '5']
      }, {
        label: '6',
        method: 'restyle',
        args: ['polynom', '6']
      }, {
        label: '7',
        method: 'restyle',
        args: ['polynom', '7']
      }, {
        label: '8',
        method: 'restyle',
        args: ['polynom', '8']
      }, {
        label: '9',
        method: 'restyle',
        args: ['polynom', '9']
      }, {
        label: '10',
        method: 'restyle',
        args: ['polynom', '10']
      }]
    }
    var windSlider = {
      len: .5,
      x: .5,
      currentvalue: {
       xanchor: 'right',
       prefix: 'Wind: ',
       font: {
         color: '#888',
         size: 10
       }
     },
      pad: {t: 210},
      steps: [{
        label: '11',
        method: 'restyle',
        args: ['wind', '11']
      }, {
        label: '13',
        method: 'restyle',
        args: ['wind', '13']
      }, {
        label: '15',
        method: 'restyle',
        args: ['wind', '15']
      }, {
        label: '17',
        method: 'restyle',
        args: ['wind', '17']
      }, {
        label: '19',
        method: 'restyle',
        args: ['wind', '19']
      }, {
        label: '21',
        method: 'restyle',
        args: ['wind', '21']
      }, {
        label: '23',
        method: 'restyle',
        args: ['wind', '23']
      }, {
        label: '25',
        method: 'restyle',
        args: ['wind', '25']
      }]
    }
    /* -----------------------------------------------------------------------------------*/

    /* ---------------Set Layout and Graph----------------------------------------------*/
    var layout = {
      xaxis: {
        rangeslider: {}
      },
      sliders: [threshSlider, minDistSlider, buffSlider, polySlider, windSlider]
    }

    Plotly.newPlot(istring, data, layout);
    /* ------------------------------------------------------------------------------------*/

    /* -----------------Set Default Slider Values-----------------------------------------*/
    var temp = [0, 0];
    xranges.push(temp);
    thresholds.push(".6");
    polynomials.push("3");
    windows.push("13");
    buffers.push("3");
    minDistances.push("5");
    /* ---------------------------------------------------------------------------------*/

    let Div = document.getElementById(istring)

    /* ----------------Range Selector----------------------------------------------*/
    Div.on('plotly_relayout', function (eventdata) {
      xranges[Div.valueOf().id][0] = eventdata['xaxis.range'][0]
      xranges[Div.valueOf().id][1] = eventdata['xaxis.range'][1]
    })
    /* ---------------------------------------------------------------------------------*/

    /* ----------------Sliders Update---------------------------------------*/
    Div.on('plotly_restyle', function(eventData){
      console.log('ello there')
      console.log(eventData[0])
      if(typeof eventData[0].thresh != "undefined"){
        thresholds[Div.valueOf().id] = eventData[0].thresh
        console.log('thresh')
        console.log(eventData[0].thresh)
        //Plotly.restyle(Div.valueOf().id, 'y', [[12, 12, 12]])
      }
      else if(typeof eventData[0].polynom != "undefined") {
        polynomials[Div.valueOf().id] = eventData[0].polynom
        console.log('poly')
        console.log(eventData[0].polynom)
        //Plotly.restyle(Div.valueOf().id, 'y', [[7,7,7]])
      }
      else if(typeof eventData[0].wind != "undefined") {
        windows[Div.valueOf().id] = eventData[0].wind
        console.log('wind')
        console.log(eventData[0].wind)
        //Plotly.restyle(Div.valueOf().id, 'y', [[7,7,7]])
      }
      else if(typeof eventData[0].buff != "undefined") {
        buffers[Div.valueOf().id] = eventData[0].buff
        console.log('buff')
        console.log(eventData[0].buff)
        //Plotly.restyle(Div.valueOf().id, 'y', [[7,7,7]])
      }
      else if(typeof eventData[0].mdist != "undefined") {
        minDistances[Div.valueOf().id] = eventData[0].mdist
        console.log('mdist')
        console.log(eventData[0].mdist)
        //Plotly.restyle(Div.valueOf().id, 'y', [[7,7,7]])
      }

      console.log(thresholds)
      console.log(buffers)
      console.log(polynomials)
      console.log(windows)
      console.log(minDistances)
	});
    /* -----------------------------------------------------------------------------------*/
  }
}



