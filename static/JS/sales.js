function renderChart(id, data, labels){
    // var ctx = document.getElementById("myChart").getContext('2d');
    var ctx = $('#' + id);
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sales per day',
                data: data,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)'
                    // 'rgba(255, 99, 132, 0.2)',
                    // 'rgba(54, 162, 235, 0.2)',
                    // 'rgba(255, 206, 86, 0.2)',
                    // 'rgba(75, 192, 192, 0.2)',
                    // 'rgba(153, 102, 255, 0.2)',
                    // 'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)'
                    // 'rgba(255,99,132,1)',
                    // 'rgba(54, 162, 235, 1)',
                    // 'rgba(255, 206, 86, 1)',
                    // 'rgba(75, 192, 192, 1)',
                    // 'rgba(153, 102, 255, 1)',
                    // 'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 3
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });
}

var url = '/analytics/sales/data/';
var data = {'type' : 'week'};

$.ajax({
    url : url,
    method : 'GET',
    data : data,
    success : function(responseData){
        console.log(data);
        renderChart('myChart', responseData.values, responseData.labels);
    },
    error : function(error){
        $.alert('An error occured');
    },
})