SELECT
    COUNT(DISTINCT sc.id) AS "Total Card Count",
    COUNT(DISTINCT ec.id) AS "Total Synergy Relationships",
    COUNT(DISTINCT cmd.id) AS "Total Commander Count",
FROM
    edhrec_cards ec
    LEFT JOIN edhrec_commanders cmd ON ec.commander_id = cmd.id
    LEFT JOIN scryfall_cards sc ON ec.card_id = sc.id