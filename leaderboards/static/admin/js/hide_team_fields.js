django.jQuery(document).ready(function () {
        function hide_fields() {
            if (django.jQuery("#id_ruleset option:selected").text() !== "team") {
                django.jQuery(".form-row.field-winner_team").hide();
                django.jQuery(".form-row.field-loser_team").hide();
                django.jQuery(".form-row.field-winner").show();
                django.jQuery(".form-row.field-loser").show();
            }
            else {
                django.jQuery(".form-row.field-winner_team").show();
                django.jQuery(".form-row.field-loser_team").show();
                django.jQuery(".form-row.field-winner").hide();
                django.jQuery(".form-row.field-loser").hide();
            }
        }

        hide_fields();
        django.jQuery("#id_ruleset").change(function () {
            hide_fields();
        });
    }
);