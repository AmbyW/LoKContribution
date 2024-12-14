

$(document).ready(function() {
    let server_data = null;
    /// 6568ab27bac8b165cca79d0b
    const paint_blocks = function (data, kingdomId=null) {
        if (data && kingdomId) {
            $("#lands").removeClass("d-none");
            $("#lands .card").each(function (index) {
                let founded = false;
                for (let land of data) {
                    if (land.position === parseInt(this.id)) {
                        $(this).find("strong").text(land.land);
                        if (land.owner === "No Owner") {
                            $(this).find("span").text(land.owner);
                        } else {
                            let kingdom_contribution = land.contributions.find(function (item) {
                                return item.kingdomId == kingdomId;
                            })
                            if (kingdom_contribution) {
                                $(this).find("span").text(kingdom_contribution.contribution.toFixed(1));
                            } else {
                                $(this).find("span").text(0);
                            }
                        }
                        $(this).css("background-color", land.color);
                        founded = true;
                        $(this).css("color", "black");
                        $(this).find("img.mr-3").removeClass("d-none");
                        //break;
                    }
                }
                if(!founded) {
                    $(this).find("strong").text(" 000 ");
                    $(this).find("span").text(" 00");
                    $(this).css("background-color", "grey");
                    $(this).css("color", "grey");
                    $(this).find("img.mr-3").addClass("d-none");
                }
            })
        }
    }
    const full_table = function (data, kingdomId=null) {

        if (data && kingdomId) {
            let html_table = '' +
            '                   <table class="table table-success table-hover table-striped table-bordered">\n' +
            '                        <thead>\n' +
            '                            <tr>\n' +
            '                                <th scope="col text-center">Owner</th>\n' +
            '                                <th scope="col text-center">Contribution</th>\n' +
            '                            </tr>\n' +
            '                        </thead>\n' +
            '                        <tbody>\n' +
            '                            {{for owners}}' +
            '                            <tr>\n' +
            '                                <td>{{>wallet}}</td>\n' +
            '                                <td>{{>contribution}} dvp</td>\n' +
            '                            </tr>\n' +
            '                            {{/for}}' +
            '                        </tbody>\n' +
            '                    </table>';
            let proc_data = {};
            proc_data["owners"] = data.owners.map(function (item) {
                return {
                    "wallet": item.wallet,
                    "contribution": item.contributions[kingdomId]
                }
            });
            let tmpl = $.templates(html_table);
            let html_rendered = tmpl.render(proc_data);
            $("#owners").removeClass("d-none");
            $("#owners .table-responsive").html(html_rendered);
        }
    }
    const fill_kingdom_name_select = function (kingdoms) {
        $('#kingdom_select').removeClass("d-none");
        kingdom_select = $('#kingdom_name').select2({
            placeholder: 'Select a Kingdom Name',
            data: kingdoms,
        });
    }

    const show_alert = function (title) {
        const topRightAlertConfig = {
            toast: true,            // Makes the alert a toast-style notification
            position: 'top-end',    // Positions the alert at the top-right
            showConfirmButton: false, // Hides the confirm button
            timer: 3000,            // Automatically closes after 3 seconds
            timerProgressBar: true, // Shows a progress bar
            width: '400px',         // Sets a specific width for the alert
            padding: '0.5rem',      // Adds some padding
            customClass: {
                popup: 'small-alert-popup',  // Custom class for additional styling
                title: 'small-alert-title',  // Custom class for the title
            },
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        }
        Swal.fire({
            ...topRightAlertConfig,
            icon: "success",
            title: title,
        });
    }

    const submit_button = $("#form_submit");
    const submit_spinner = $("#form_spinner")
    const enable_spinner = function () {
        submit_button.addClass("d-none");
        submit_spinner.removeClass("d-none");
    }

    const hide_result_section = function () {
        $('#kingdom_select').addClass("d-none");
        $("#owners").addClass("d-none");
        $("#lands").addClass("d-none");
        kingdom_select.val("");
    }

    const disable_spinner = function () {
        submit_button.removeClass("d-none");
        submit_spinner.addClass("d-none");
    }
    let kingdom_select = $('#kingdom_name').select2({
        placeholder: 'Select a Kingdom Name'
    });
    let form = $("#getcontribution-form");
    $("#adjacent_lands").on("change", function (e) {
        hide_result_section();
    })
    kingdom_select.on("change", function (e) {
        if (server_data) {
            let selected = $(this).val();
            paint_blocks(server_data.lands, selected);
            full_table(server_data, selected);
        }
    })
    $("#from").datepicker({
        format: 'yyyy-mm-dd',
        endDate: "today",
    });
    $("#to").datepicker({
        format: 'yyyy-mm-dd',
        endDate: "today",
    });
    $.validator.addMethod("greaterThan",
        function(value, element, params) {

            if (!/Invalid|NaN/.test(new Date(value))) {
                if ($(params).val())
                    return new Date(value) >= new Date($(params).val());
                return true;
            }

            return isNaN(value) && isNaN($(params).val())
                || (Number(value) >= Number($(params).val()));
    },'Must be greater than to date');
    $.validator.addMethod("lowerThan",
        function(value, element, params) {

            if (!/Invalid|NaN/.test(new Date(value))) {
                if ($(params).val())
                    return new Date(value) <= new Date($(params).val());
                return true;
            }

            return isNaN(value) && isNaN($(params).val())
                || (Number(value) <= Number($(params).val()));
    },'Must be greater than from date');
    $.validator.addMethod("DatesDifference31",
    function (value, element, params) {

            if (!/Invalid|NaN/.test(new Date(value))) {
                if ($(params).val()) {
                    let date1 = new Date(value);
                    let date2 = new Date($(params).val());
                    const difference = Math.abs(date1 - date2);
                    const daysDifference = Math.floor(difference / (1000 * 60 * 60 * 24));
                    return daysDifference <= 31;
                }
                return true;
            }

            return isNaN(value) && isNaN($(params).val())
                || (Number(value) <= Number($(params).val()));

    }, 'Dates difference should be lower or equal to 31 days');
    form.validate({
        errorClass: 'text-danger',
        rules: {
            'land_id': {
                required: true,
                digits: true,
                min: 100000,
                max: 165535,
                maxlength: 6,
                minlength: 6,
            },
            'from': {
                required: true,
                lowerThan: '#to',
                DatesDifference31: '#to',
            },
            'to': {
                greaterThan: '#from',
                DatesDifference31: '#from',
                required: true,
            },
        },
    });
    form.on("submit", function (e) {
        e.preventDefault();
        if (!form.valid()) {
            return;
        }
        let data = [];
        form.find('input,select').each(function() {
            if (this.type === 'checkbox')
                data.push({name: this.name, value: this.checked});
            else
                data.push({name: this.name, value: this.value});
        });
        enable_spinner();
        hide_result_section();
        $.ajax({
            type: "GET",
            url: '/get_contribution',
            data: data,
            success: function (response) {
                disable_spinner();
                server_data = response;
                show_alert("Data fetched successfully, please select a kingdom name from the list to check the contribution")
                fill_kingdom_name_select(response.kingdoms)
            },
            error: function (errors) {
                console.log(errors);
                disable_spinner();
            }
        })
    })
})