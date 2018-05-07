$(document).ready(function(){
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
    .sortableTable('addView', 'plane-plate', function(value){
      return {
        html: '<code>' + value + '</code>'
      };
    })
    .sortableTable('view');
});