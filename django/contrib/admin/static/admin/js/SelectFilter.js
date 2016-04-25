(function($) {
var settings = {
    'name': '',
    'verbose_name': '',
    'is_stacked': 0,
    'admin_media_prefix': '',
    'select': function select(options, from, to) {
        SelectBox.move(from.attr('id'), to.attr('id'));
        SelectBox.sort(to.attr('id'));
        SelectBox.redisplay(to.attr('id'));
    },
    'deselect': function deselect(options, from, to) {
        SelectBox.move(from.attr('id'), to.attr('id'));
        SelectBox.sort(to.attr('id'));
        SelectBox.redisplay(to.attr('id'));
    }
};

var methods = {
    init: function(options) {
        $.extend(settings, options);
        var choices = this;
        var stack_class = settings.is_stacked ? 'selector stacked' : 'selector';
        var selector = $('<div>').addClass(stack_class);

        choices.parent().append(selector);
        choices.attr({
            'id': choices.attr('id') + '_from',
            'name': choices.attr('name') + '_old'
        });

        var search = $('<input>').attr({
            'id': 'id_' + settings.name + '_input',
            'type': 'text'
        });

        $('<div>').addClass('selector-available')
            .append($('<h2>').text(gettext('Available ') + settings.verbose_name))
            .append(
                $('<p>').addClass('selector-filter')
                    .append(
                        $('<label>').attr('for', search.attr('id')).css({'width': "16px", 'padding': "2px"})
                            .append(
                                $('<img>').attr('src', settings.admin_media_prefix + 'img/admin/selector-search.gif')
                            )
                    )
                    .append(search)
            ).append(choices)
            .append($('<a>').addClass('selector-chooseall').text(gettext('Choose all')).attr('href', '#'))
            .appendTo(selector);

        $('<ul>').addClass('selector-chooser')
            .append($('<li>')
                .append($('<a>').addClass('selector-add').text(gettext('Add')))
            )
            .append($('<li>')
                .append($('<a>').addClass('selector-remove').text(gettext('Remove')))
            )
            .appendTo(selector);

        var selected = $('<select>').addClass('filtered').attr({
            'id': 'id_' + settings.name + '_to',
            'multiple': 'multiple',
            'name': settings.name
        });

        $('<div>').addClass('selector-chosen')
            .append($('<h2>').text('Chosen ' + settings.verbose_name))
            .append(
                $('<p>').addClass('selector-filter')
                    .text(gettext('Select your choice(s) and click '))
                    .append(
                        $('<img>').attr({
                            'src': settings.admin_media_prefix + 'img/admin/selector-add.gif',
                            'alt': gettext('Add')
                        })
                    )
            ).append(selected)
            .append(
                $('<a>').addClass('selector-clearall')
                    .text(gettext('Clear all'))
                    .attr('href', '#')
            ).appendTo(selector);

        SelectBox.init(choices.attr('id'));
        SelectBox.init(selected.attr('id'));

        // If this is a saved instance, move the already selected options across
        // to the selected list.
        settings.select(choices.children().filter(':selected'), choices, selected);

        // Hook up selection events.
        $(search).keyup(function(event) {
            if ((event.which && event.which == 13) || (event.keyCode && event.keyCode == 13)) {
                settings.select(choices.children().filter(':selected'), choices, selected);
                return false;
            }
            SelectBox.filter(choices.attr('id'), $(this).val());
            return true;
        });
        $('.selector-chooseall').click(function() {
            settings.select(choices.children(), choices, selected);
            return false;
        });

        $('.selector-clearall').click(function() {
            settings.deselect(selected.children(), selected, choices);
            return false;
        });

        $('.selector-add').click(function() {
            settings.select(choices.children().filter(':selected'), choices, selected);
            return false;
        });

        $('.selector-remove').click(function() {
            settings.deselect(selected.children().filter(':selected'), selected, choices);
            return false;
        });

        choices.dblclick(function() {
            settings.select(choices.children().filter(':selected'), choices, selected);
        });

        selected.dblclick(function() {
            settings.deselect(selected.children().filter(':selected'), selected, choices);
        });

        choices.keydown(function(event) {
            event.which = event.which ? event.which : event.keyCode;
            switch(event.which) {
                case 13:
                    // Enter pressed - don't submit the form but move the current selection.
                    settings.select(choices.children().filter(':selected'), choices, selected);
                    this.selectedIndex = (this.selectedIndex == this.length) ? this.length - 1 : this.selectedIndex;
                    return false;
                case 39:
                    // Right arrow - move across (only when horizontal)
                    if (!settings.is_stacked) {
                        settings.select(choices.children().filter(':selected'), choices, selected);
                        this.selectedIndex = (this.selectedIndex == this.length) ? this.length - 1 : this.selectedIndex;
                        return false;
                    }
            }
            return true;
        });

        selected.keydown(function(event) {
            event.which = event.which ? event.which : event.keyCode;
            switch(event.which) {
                case 13:
                    // Enter pressed - don't submit the form but move the current selection.
                    settings.select(selected.children().filter(':selected'), selected, choices);
                    this.selectedIndex = (this.selectedIndex == this.length) ? this.length - 1 : this.selectedIndex;
                    return false;
                case 37:
                    // Left arrow - move across (only when horizontal)
                    if (!settings.is_stacked) {
                        settings.select(selected.children().filter(':selected'), selected, choices);
                        this.selectedIndex = (this.selectedIndex == this.length) ? this.length - 1 : this.selectedIndex;
                        return false;
                    }
            }
            return true;
        });

        $('form').submit(function() {
            selected.children().each(function(i, option) {
                $(option).attr('selected', 'selected');
            });
            return true;
        });
    }
};

$.fn.selectFilter = function(method) {
    if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } else if (typeof method === 'object' || !method ) {
        return methods.init.apply(this, arguments);
    } else {
        $.error('Method ' + method + ' does not exist on jQuery.selectFilter');
    }
};
})(django.jQuery);