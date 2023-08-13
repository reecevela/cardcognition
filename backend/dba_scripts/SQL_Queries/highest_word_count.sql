WITH WordCounts AS (
    SELECT card_name,
           LENGTH(oracle_text) - LENGTH(REPLACE(oracle_text, ' ', '')) + 1 AS word_count
    FROM scryfall_cards
    WHERE oracle_text IS NOT NULL
)
SELECT wc.card_name, wc.word_count, sc.oracle_text
FROM WordCounts wc
INNER JOIN scryfall_cards sc
ON sc.card_name = wc.card_name
ORDER BY wc.word_count DESC
LIMIT 10;