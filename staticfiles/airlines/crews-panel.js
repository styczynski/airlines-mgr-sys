$(document).ready(function(){
  var crewsTableNav = $('nav.pages');
  var crewsTable = $('table.crews-table');
  var crewsTableBody = crewsTable.find('tbody');
  
  var PAGE_SIZE = 30;
  
  var pageNo = getParameterByName('page');
  var pageOffset = '';
  if(pageNo) {
    pageNo = parseInt(pageNo);
    pageOffset = pageNo*PAGE_SIZE; 
  } else {
    pageNo = 0;
  }
  
  
  function renderCrewsTable(flightsApiURL){
    
    var flightsApiURL = `flights?offset=${pageOffset}`;
    
    crewsTableBody.children().remove();
    crewsTableNav.children().remove();
    
    function renderRowContent(crewsRow, flight, flightIndex) {
      crewsRow = $(crewsRow);
      crewsRow.children().remove();
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
    };
    
    function updateRow(crewsRow, flightIndex) {
      requestDataAPI('flights', function(flights){
        var flight = flights[flightIndex];
        if(!flight) return;
        crewsTableBody.find('.content-expanded').remove();
        renderRowContent(crewsRow, flight, flightIndex);
        crewsTable.sortableTable('view');
      });
    };
    
    checkUserAuth(function(userAuth){
      
      if(userAuth) {
        $('header > nav').children().remove();
        $('header > nav').append(`
          Logged as <span class="username">${userAuth.username}</span>
          <a href="logout">
            <button class="small">
              Logout
            </button>
          </a>
        `);
      }
      
      requestDataAPI(flightsApiURL, function(flights, flightsRes){
        
        flights.forEach(function(flight, flightIndex){
          var crewsRow = $(`<tr></tr>`);
          renderRowContent(crewsRow, flight, flightIndex);
          crewsRow.appendTo(crewsTable);
        });
        
        
        var navLast = '';
        if(parseInt(flightsRes.count/PAGE_SIZE) != pageNo) {
          navLast = `
            <li>
              <a href="crews-panel?page=${parseInt(flightsRes.count/PAGE_SIZE)}">
                &gt;&gt;
              </a>
            </li>
          `;
        }
        
        var navNext = '';
        if(flightsRes.next) {
          navNext = `
            <li>
              <a href="crews-panel?page=${pageNo+1}">
                &gt;
              </a>
            </li>
          `;
        }
        
        var navLeft = '';
        for(var p=pageNo-5;p<pageNo;++p) {
          if(p>=0 && p*PAGE_SIZE+(PAGE_SIZE-1) <= flightsRes.count) {
            navLeft += `
              <li>
                <a href="crews-panel?page=${p}">
                  ${p+1}
                </a>
              </li>
            `;
          }
        }
        
        var navRight = '';
        for(var p=pageNo+1;p<=pageNo+5;++p) {
          if(p>=0 && p*PAGE_SIZE+(PAGE_SIZE-1) <= flightsRes.count) {
            navRight += `
              <li>
                <a href="crews-panel?page=${p}">
                  ${p+1}
                </a>
              </li>
            `;
          }
        }
        
        var navCurrent = `
          <li class="active">
            <a href="crews-panel?page=${pageNo}">
              ${pageNo+1}
            </a>
          </li>
        `;
        
        var navPrev = '';
        if(flightsRes.previous) {
          navPrev = `
            <li>
              <a href="crews-panel?page=${pageNo-1}">
                &lt;
              </a>
            </li>
          `;
        }
        
        var navFirst = '';
        if(pageNo != 0) {
          navFirst = `
            <li>
              <a href="crews-panel?page=0">
                &lt;&lt;
              </a>
            </li>
          `;
        }
        
        crewsTableNav.append(`
         <ul>
            ${navFirst}
            ${navPrev}
            ${navLeft}
            ${navCurrent}
            ${navRight}
            ${navNext}
            ${navLast}
          </ul>
        `);
        
        crewsTable
        .sortableTable('addView', 'plane-plate', function(value){
          return {
            html: '<code>' + value + '</code>'
          };
        })
        .sortableTable('view')
        .sortableTable('rowClick', function(row, table, context) {
          if(context !== null) {
            context = parseInt(context) || 0;
            var flightForRow = flights[context];
            
            crewsTableBody.find('.content-expanded').remove();
            
            var tableRow = crewsTableBody.find('tr')[context];
            var expandedContent = $('<tr></tr>');
            expandedContent.attr('colspan', 6);
            expandedContent.addClass('content-expanded');
            expandedContent.addClass('no-hover');
            
            function changeCrewTo(newCrew) {
              
              patchDataAPI(`flights/update/${flightForRow.id}/`, {
                'crew': newCrew.id
              }, function(res){
                updateRow(tableRow, context);
              })
            };
            
            var expandedContentData = $('<td></td>');
            expandedContentData.attr('colspan', 6);
            
            var restrictedArea = '';
            
            if(userAuth) {
              restrictedArea = `
                <button class="button-crew small">
                   <i class="fas fa-users"></i>
                   Change flight crew
                </button>
              `;
            }
            
            expandedContentData.append(`
              ${restrictedArea}
              <button class="button-edit small">
                 <i class="fas fa-info-circle"></i>
                 Flight details
              </button>
              <div class="details">
                <ul>
                  <li>Departure: ${flightForRow.departure}</li>
                  <li>Arrival: ${flightForRow.departure}</li>
                  <li>Sold tickets: ${flightForRow.tickets.length / flightForRow.plane.seats_count} %</li>
                </ul>
              </div>
              <div class="edit-box"></div>
            `);
            
            expandedContentData.find('.button-edit').click(function(){
              window.location = `/flight-edit?id=${flightForRow.id}&back=crewsPanel`;
            });
            
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
  
  };
  
  renderCrewsTable();
  
});