$(document).ready(function () {
    /*$('table')
      .sortableTable('addView', 'plane-plate', function(value){
        return {
          html: '<code>' + value + '</code>'
        };
      })
      .sortableTable('init')
      .sortableTable('view')
      .sortableTable('rowClick', function(row) {
        console.log('row handler');
        console.log(row);
    });*/
    $('table')
        .sortableTable('addView', 'plane-plate', function (value) {
            return {
                html: '<code>' + value + '</code>'
            };
        })
        .sortableTable('view')
        .sortableTable('rowClick', function (row, table, context) {
            if (context) {
                //window.location = 'flight-edit?id='+context+'&back='+encodeURIComponent(window.location);
                window.location = context;//'flight-edit?id='+context+'&back=flightEdit';
            }
        });
});
