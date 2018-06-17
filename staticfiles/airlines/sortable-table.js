var SortableTable = {};

(function ($) {

    var isInited = false;

    var defaultStringConverter = function (value) {
        return value.toString();
    };

    var views = {
        'from-now': function (value) {
            return value.fromNow();
        },

        'to-now': function (value) {
            return value.toNow();
        },

        'percentage': function (value) {
            var str = parseFloat(value.toString()) / 100.0;
            if (str[str.length - 1] != '%') {
                str += '%';
            }
            return str;
        },

        'date': function (value, opts) {
            if (window.moment) {
                if (opts.output) {
                    return value.format(opts.output);
                }
                return value.toString();
            }
            return value;
        }

    };

    var types = {
        'date': {
            converter: function (value, opts) {
                if (window.moment) {
                    if (opts.input) {
                        return window.moment(value, opts.input);
                    }
                    return window.moment(value);
                }
                return +(Date.parse(value));
            },
            comparator: function (valueA, valueB) {
                return valueA.unix() < valueB.unix();
            }
        },

        'timestamp': {
            converter: function (value) {
                if (window.moment) {
                    return window.moment(value, 'X');
                }
                return +(Date.parse(value));
            },
            comparator: function (valueA, valueB) {
                return valueA.unix() < valueB.unix();
            }
        },

        'string': {
            converter: defaultStringConverter
        },

        'integer': {
            converter: function (value) {
                return parseInt(value.toString().replace(/[,\.]/ig, ''));
            }
        },

        'float': {
            converter: function (value) {
                return parseFloat(value.toString().replace(/[,\.]/ig, '.'));
            }
        },

        'percentage': {
            converter: function (value) {
                return parseFloat(value.toString().replace(/%/ig, '').replace(/[,\.]/ig, '.'));
            }
        }
    };

    var castToType = function (type, value, opts) {
        if (types[type]) {
            var data = types[type].converter(value, opts);
            return {
                type: type,
                value: data
            };
        }
        return {
            type: 'string',
            value: value
        };
    };

    var cmpDefaultValuesGt = function (valueA, valueB) {
        return valueA.value > valueB.value ? -1 : valueA.value < valueB.value ? 1 : 0;
    };

    var cmpValuesGt = function (valueA, valueB) {
        if (types[valueA.type]) {
            if (types[valueA.type].comparator) {
                var cmpValue = types[valueA.type].comparator(valueA.value, valueB.value);
                return cmpValue ? -1 : 1;
            }
        }
        return cmpDefaultValuesGt(valueA, valueB);
    };

    var cmpValuesLt = function (valueA, valueB) {
        return -cmpValuesGt(valueA, valueB);
    };

    var extractRowColText = function (rowObj, colNo) {
        var rowColObj = $($(rowObj).children()[colNo]);
        if (rowColObj.data('content')) {
            return rowColObj.data('content');
        }
        return rowColObj.text();
    };

    var renderRowColView = function (rowObj, colNo, viewType, type, convOpts) {
        var rowColObj = $($(rowObj).children()[colNo]);
        var content = extractRowColText(rowObj, colNo);

        var colA = castToType(type, content, convOpts);

        rowColObj.attr('data-content', content);
        if (views[viewType]) {
            var viewContent = views[viewType](colA.value, convOpts);
            if (viewContent.html) {
                rowColObj.html(viewContent.html);
            } else {
                rowColObj.text(viewContent);
            }
        }
    };

    var collectOpts = function (element) {
        var inputOpt = $(element).data('input');
        var outputOpt = $(element).data('output');
        var convOpts = {
            input: inputOpt,
            output: outputOpt
        };
        return convOpts;
    };

    var SorTable = {

        addType: function (name, converter, comparator) {
            if (!converter) {
                converter = defaultStringConverter;
            }
            types[name.toString()] = {
                converter: converter,
                comparator: comparator
            }
            return SorTable;
        },

        getType: function (name) {
            return types[name.toString()];
        },

        addView: function (name, fn) {
            views[name] = fn;
        },

        getView: function (name) {
            return views[name.toString()];
        },

        __document_init: function () {
            if (!isInited) {
                SorTable.init('table');
            }
        },

        rowClick: function (selector, handler) {
            if (!$) {
                throw "JQuery is needed to be loaded before sortable-table utility is used.";
            }

            if (!handler) return;

            $(selector).each(function (index) {
                var table = $(this);
                var tableHead = table.find('th');
                var tableBody = table.find('tbody');

                tableBody.on('click', 'tr', function () {
                    var clickedElement = $(this);

                    var rowData = {};
                    tableHead.each(function (thIndex) {
                        var type = $(this).data('type') || 'string';
                        var name = $(this).data('name') || $(this).text().trim();
                        var colA = extractRowColText(clickedElement, thIndex);

                        var convOpts = collectOpts(this);
                        colA = castToType(type, colA, convOpts);
                        rowData[name] = colA.value;
                    });

                    var context = clickedElement.data('context');
                    if (context === null || typeof context === 'undefined') {
                        context = null;
                    }

                    handler(rowData, table, context);
                });
            });
        },

        initViews: function (selector) {
            if (!$) {
                throw "JQuery is needed to be loaded before sortable-table utility is used.";
            }

            $(selector).each(function (index) {
                var table = $(this);

                table.find('th').each(function (i) {
                    var self = $(this);
                    var tableBody = table.find('tbody');
                    var sortingType = self.data('type') || 'string';

                    var convOpts = collectOpts(this);

                    if (self.data('view')) {
                        tableBody.find('tr').each(function () {
                            var rowObj = $(this);
                            renderRowColView(rowObj, i, self.data('view'), sortingType, convOpts);
                        });
                    }
                });
            });
        },

        init: function (selector) {
            if (!$) {
                throw "JQuery is needed to be loaded before sortable-table utility is used.";
            }

            isInited = true;

            $(selector).each(function (index) {
                var table = $(this);

                table.find('th').each(function (i) {
                    var self = $(this);
                    var tableBody = table.find('tbody');
                    var sortingType = self.data('type') || 'string';
                    var sortingMode = self.data('mode') || 'toggle';

                    var convOpts = collectOpts(this);

                    if (sortingMode == 'off') return;

                    (function (thIndex, type, mode) {
                        var sortOnClick = (function () {
                            var currentMode = self.data('current-mode');
                            var sortedRows = tableBody.find('tr').sort(function (rowA, rowB) {
                                var colA = extractRowColText(rowA, thIndex);
                                var colB = extractRowColText(rowB, thIndex);
                                colA = castToType(type, colA, convOpts);
                                colB = castToType(type, colB, convOpts);
                                if (mode == 'toggle') {
                                    if (currentMode == 'asc') {
                                        return cmpValuesGt(colA, colB);
                                    }
                                    return cmpValuesLt(colA, colB);
                                } else if (mode == 'asc') {
                                    return cmpValuesGt(colA, colB);
                                }
                                return cmpValuesLt(colA, colB);
                            });
                            table.find('th').removeClass('sort-asc').removeClass('sort-desc');

                            if (mode == 'toggle') {
                                if (currentMode == 'asc') {
                                    self.data('current-mode', 'desc');
                                    self.addClass('sort-desc');
                                } else {
                                    self.data('current-mode', 'asc');
                                    self.addClass('sort-asc');
                                }
                            } else if (mode == 'asc') {
                                self.data('current-mode', 'asc');
                                self.addClass('sort-asc');
                            } else if (mode == 'desc') {
                                self.data('current-mode', 'desc');
                                self.addClass('sort-desc');
                            }
                            sortedRows.appendTo(tableBody);
                        });
                        self.click(sortOnClick);

                        // Initially sorts the data
                        sortOnClick();
                    }(i, sortingType, sortingMode));
                });
            });
        }
    };

    window.SortableTable = SortableTable = SorTable;
    $.fn.sortableTable = function (action, arg1, arg2, arg3) {
        var element = this;
        action = action || 'init';
        if (action == 'init') {
            SorTable.init(element || 'table');
        } else if (action == 'addType') {
            SorTable.addType(arg1, arg2, arg3);
        } else if (action == 'getType') {
            return SorTable.getType(arg1);
        } else if (action == 'addView') {
            SorTable.addView(arg1, arg2);
        } else if (action == 'getView') {
            return SorTable.getView(arg1);
        } else if (action == 'rowClick') {
            SorTable.rowClick(element || 'table', arg1);
        } else if (action == 'view') {
            SorTable.initViews(element || 'table');
        }
        return this;
    };

})(jQuery);