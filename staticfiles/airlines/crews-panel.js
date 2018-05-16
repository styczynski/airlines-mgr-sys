$(document).ready(function(){
  var crewsTable = $('table.crews-table');
  var crewsTableBody = crewsTable.find('tbody');
  console.log(crewsTable);
  
  requestDataAPI('flights', function(flights){
    flights.forEach(function(flight, flightIndex){
      var crewsRow = $(`<tr></tr>`);
      crewsRow.attr('data-context', flightIndex);
      crewsRow.append(`<td>${flight.plane.reg_id}</td>`);
      
      if(flight.crew) {
        crewsRow.append(`<td><code>${flight.crew.crew_id}</code> (${flight.crew.worker_set.length} workers)</td>`);
      } else {
        crewsRow.append(`<td>No crew</td>`);
      }
      
      crewsRow.append(`<td>${flight.src}</td>`);
      crewsRow.append(`<td>${flight.dest}</td>`);
      crewsRow.append(`<td>${flight.departure}</td>`);
      crewsRow.append(`<td>${flight.arrival}</td>`);
      crewsRow.appendTo(crewsTable);
    });
    
    crewsTable
    .sortableTable('addView', 'plane-plate', function(value){
      return {
        html: '<code>' + value + '</code>'
      };
    })
    .sortableTable('view')
    .sortableTable('rowClick', function(row, table, context) {
      if(context) {
        context = parseInt(context) || 0;
        var flightForRow = flights[context];
        
        crewsTableBody.find('.content-expanded').remove();
        
        var tableRow = crewsTableBody.find('tr')[context];
        var expandedContent = $('<tr></tr>');
        expandedContent.attr('colspan', 6);
        expandedContent.addClass('content-expanded');
        expandedContent.addClass('no-hover');
        
        function changeCrewTo(newCrew) {
          console.log('change crew of ');
          console.log(flightForRow);
          console.log('to');
          console.log(newCrew);
          
          ////PATCH /airlines/api/flights/update/2/
          patchDataAPI(`flights/update/${flightForRow.id}/`, {
            'crew': newCrew.id
          }, function(res){
            console.log('respond');
            console.log(res);
          })
        };
        
        var expandedContentData = $('<td></td>');
        expandedContentData.attr('colspan', 6);
        
        expandedContentData.append(`
          <button class="button-crew small">
             <i class="fas fa-ban"></i>
             Change flight crew
          </button>
          <button class="small">
             <i class="fas fa-ban"></i>
             Edit flight
          </button>
          <div class="edit-box"></div>
        `);
        
        expandedContentData.find('.button-crew').click(function(){
          var editBox = expandedContentData.find('.edit-box');
          editBox.children().remove();
          editBox.append(`
            <input type='text' name='crew' placeholder='${row.Crew}'>
            <ul class='input-suggestions'></ul>
          `);
          
          var crewSugg = editBox.find('.input-suggestions');
          var crewInput = editBox.find('input');
          crewInput.on('input', function(){
            var val = crewInput.val();
            requestDataAPI(`crews/search/${val}`, function(suggestions){
              crewSugg.children().remove();
              crewSugg.append(suggestions.map(function(crew){
                var option = $(`
                  <li>
                    <code>${crew.crew_id}</code>
                    <b>Crew</b>
                    <ul>
                      <li>Currently added to ${crew.flight_set.length} flights</li>
                    </ul>
                    <ul>
                      <li>${crew.worker_set.length} worker/-s</li>
                    </ul>
                  </li>
                `);
                option.click(function(){
                  crewInput.val(crew.crew_id);
                  editBox.children().remove();
                  changeCrewTo(crew);
                });
                return option;
              }));
            });
          });
        })
        
        expandedContentData.appendTo(expandedContent);
        expandedContent.insertAfter(tableRow);
      }
    });
  });
  
});