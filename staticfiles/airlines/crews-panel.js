$(document).ready(function () {
    var crewsTableNav = $('nav.pages');
    var crewsTable = $('table.crews-table');
    var crewsTableBody = crewsTable.find('tbody');

    var PAGE_SIZE = 30;

    var pageNo = getParameterByName('page');
    var pageOffset = '';
    if (pageNo) {
        pageNo = parseInt(pageNo);
        pageOffset = pageNo * PAGE_SIZE;
    } else {
        pageNo = 0;
    }

    function extractPositiveNumParm(name) {
        if (getParameterByName(name)) {
            if (parseInt(getParameterByName(name))) {
                //console.log(name+" = "+parseInt(getParameterByName(name)));
                return parseInt(getParameterByName(name));
            }
        }
        //console.log(name+" = ?");
        return null;
    };

    var filterMomentFrom = null;
    if (extractPositiveNumParm('from_date_year')) {
        var val = extractPositiveNumParm('from_date_year');
        if(!filterMomentFrom) filterMomentFrom = moment();
        filterMomentFrom.year(val);
        $('form.filter select[name="from_date_year"]').val(val);
    }
    if (extractPositiveNumParm('from_date_month')) {
        var val = extractPositiveNumParm('from_date_month');
        if(!filterMomentFrom) filterMomentFrom = moment();
        filterMomentFrom.month(val - 1);
        $('form.filter select[name="from_date_month"]').val(val);
    }
    if (extractPositiveNumParm('from_date_day')) {
        var val = extractPositiveNumParm('from_date_day');
        if(!filterMomentFrom) filterMomentFrom = moment();
        filterMomentFrom.date(val);
        $('form.filter select[name="from_date_day"]').val(val);
    }

    var filterMomentTo = null;
    if (extractPositiveNumParm('to_date_year')) {
        var val = extractPositiveNumParm('to_date_year');
        if(!filterMomentTo) filterMomentTo = moment();
        filterMomentTo.year(val);
        $('form.filter select[name="to_date_year"]').val(val);
    }
    if (extractPositiveNumParm('to_date_month')) {
        var val = extractPositiveNumParm('to_date_month');
        if(!filterMomentTo) filterMomentTo = moment();
        filterMomentTo.month(val - 1);
        $('form.filter select[name="to_date_month"]').val(val);
    }
    if (extractPositiveNumParm('to_date_day')) {
        var val = extractPositiveNumParm('to_date_day');
        if(!filterMomentTo) filterMomentTo = moment();
        filterMomentTo.date(val);
        $('form.filter select[name="to_date_day"]').val(val);
    }

    var dateFiltering = {
        'from': (filterMomentFrom) ? (filterMomentFrom.format('YYYY-MM-DD')) : (null),
        'to': (filterMomentTo) ? (filterMomentTo.format('YYYY-MM-DD')) : (null)
    };


    //$('form.filter input[type="submit"]').click(function(e){
    //console.log('submit');
    //var formData = $('form.filter').serialize();
    //console.log(formData);
    //e.preventDefault();
    //return false;
    //});


    function renderCrewsTable(flightsApiURL) {

        var flightsApiURL = `flights?offset=${pageOffset}`;

        if (dateFiltering.from) {
            flightsApiURL += `&from=${dateFiltering.from}`;
        }

        if (dateFiltering.to) {
            flightsApiURL += `&to=${dateFiltering.to}`;
        }

        crewsTableBody.children().remove();
        crewsTableNav.children().remove();

        function renderRowContent(crewsRow, flight, flightIndex) {
            crewsRow = $(crewsRow);
            crewsRow.children().remove();
            crewsRow.attr('data-context', flightIndex);
            crewsRow.append(`<td>${flight.plane.reg_id}</td>`);

            if (flight.crew) {
                crewsRow.append(`<td><code>${flight.crew.crew_name}</code> (${flight.crew.worker_set.length} workers)</td>`);
            } else {
                crewsRow.append(`<td>No crew</td>`);
            }

            crewsRow.append(`<td>${flight.src}</td>`);
            crewsRow.append(`<td>${flight.dest}</td>`);
            crewsRow.append(`<td>${flight.departure}</td>`);
            crewsRow.append(`<td>${flight.arrival}</td>`);
        };

        function updateRow(crewsRow, flightIndex) {
            requestDataAPI('flights', function (flights) {
                var flight = flights[flightIndex];

                if (!flight) return;
                crewsTableBody.find('.content-expanded').remove();
                renderRowContent(crewsRow, flight, flightIndex);
                crewsTable.sortableTable('view');
            });
        };

        checkUserAuth(function (userAuth) {

            if (userAuth) {
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

            requestDataAPI(flightsApiURL, function (flights, flightsRes) {

                flights.forEach(function (flight, flightIndex) {
                    var crewsRow = $(`<tr></tr>`);
                    renderRowContent(crewsRow, flight, flightIndex);
                    crewsRow.appendTo(crewsTable);
                });


                var navLast = '';
                if (parseInt(flightsRes.count / PAGE_SIZE) != pageNo) {
                    navLast = `
            <li>
              <a href="crews-panel?page=${parseInt(flightsRes.count / PAGE_SIZE)}">
                &gt;&gt;
              </a>
            </li>
          `;
                }

                var navNext = '';
                if (flightsRes.next) {
                    navNext = `
            <li>
              <a href="crews-panel?page=${pageNo + 1}">
                &gt;
              </a>
            </li>
          `;
                }

                var navLeft = '';
                for (var p = pageNo - 5; p < pageNo; ++p) {
                    if (p >= 0 && p * PAGE_SIZE + (PAGE_SIZE - 1) <= flightsRes.count) {
                        navLeft += `
              <li>
                <a href="crews-panel?page=${p}">
                  ${p + 1}
                </a>
              </li>
            `;
                    }
                }

                var navRight = '';
                for (var p = pageNo + 1; p <= pageNo + 5; ++p) {
                    if (p >= 0 && p * PAGE_SIZE + (PAGE_SIZE - 1) <= flightsRes.count) {
                        navRight += `
              <li>
                <a href="crews-panel?page=${p}">
                  ${p + 1}
                </a>
              </li>
            `;
                    }
                }

                var navCurrent = `
          <li class="active">
            <a href="crews-panel?page=${pageNo}">
              ${pageNo + 1}
            </a>
          </li>
        `;

                var navPrev = '';
                if (flightsRes.previous) {
                    navPrev = `
            <li>
              <a href="crews-panel?page=${pageNo - 1}">
                &lt;
              </a>
            </li>
          `;
                }

                var navFirst = '';
                if (pageNo != 0) {
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
                    .sortableTable('addView', 'plane-plate', function (value) {
                        return {
                            html: '<code>' + value + '</code>'
                        };
                    })
                    .sortableTable('view')
                    .sortableTable('rowClick', function (row, table, context) {
                        if (context !== null) {
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
                                }, function (res) {
                                    showMessage({
                                        message: 'Updated flight data successfully.',
                                        messageType: 'info'
                                    });
                                    setTimeout(function() {
                                        updateRow(tableRow, context);
                                    }, 700);
                                }, function(err) {
                                    let errMessage = 'Unknown server error occurred.'
                                    if(err) {
                                        if(err.detail) {
                                            errMessage = err.detail;
                                        }
                                    }
                                    console.log(errMessage);
                                    showMessage({
                                        message: (errMessage || '').replace(/\n/ig, '<br>'),
                                        messageType: 'error',
                                        autoHide: false
                                    });
                                })
                            };

                            var expandedContentData = $('<td></td>');
                            expandedContentData.attr('colspan', 6);

                            var restrictedArea = '';

                            if (userAuth) {
                                restrictedArea = `
                <button class="button-crew small">
                   <i class="fas fa-users"></i>
                   Change flight crew
                </button>
              `;
                            }

                            var detailsTextDep = moment.unix(parseInt(flightForRow.departure)).toNow();
                            var detailsTextArr = moment.unix(parseInt(flightForRow.departure)).fromNow();
                            var detailsTextSoldPerc = parseInt(flightForRow.tickets.length / flightForRow.plane.seats_count * 100) / 100;

                            expandedContentData.append(`
              <div class="flight-details-table">
                <table>
                  <tr>
                    <td>Departure:</td>
                    <td>${detailsTextDep}</td>
                  </tr>
                  <tr>
                    <td>Arrival:</td>
                    <td>${detailsTextArr}</td>
                  </tr>
                  <tr>
                    <td>Sold tickets:</td>
                    <td>${flightForRow.tickets.length} (${detailsTextSoldPerc}%)</td>
                  </tr>
                </table>
              </div>
              ${restrictedArea}
              <button class="button-edit small">
                 <i class="fas fa-info-circle"></i>
                 Flight details
              </button>
              <div class="edit-box"></div>
            `);

                            expandedContentData.find('.button-edit').click(function () {
                                window.location = `/airlines/flight-edit/?id=${flightForRow.id}&back=crewsPanel`;
                            });

                            expandedContentData.find('.button-crew').click(function () {
                                var editBox = expandedContentData.find('.edit-box');
                                editBox.children().remove();
                                editBox.append(`
                <input type='text' name='crew' placeholder='${row.Crew}'>
                <ul class='input-suggestions'></ul>
              `);

                                var crewSugg = editBox.find('.input-suggestions');
                                var crewInput = editBox.find('input');
                                crewInput.on('input', function () {
                                    var val = crewInput.val();
                                    requestDataAPI(`crews/search/${val}`, function (suggestions) {
                                        crewSugg.children().remove();
                                        crewSugg.append(suggestions.map(function (crew) {
                                            var option = $(`
                      <li>
                        <code>${crew.crew_name}</code>
                        <b>Crew</b>
                        <ul>
                          <li>Currently added to ${crew.flight_set.length} flights</li>
                        </ul>
                        <ul>
                          <li>${crew.worker_set.length} worker/-s</li>
                        </ul>
                      </li>
                    `);
                                            option.click(function () {
                                                crewInput.val(crew.crew_name);
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