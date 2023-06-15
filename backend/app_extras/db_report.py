import sql_executer

# print number of unique card_names
print(f"Unique Cards: {sql_executer.sql_executer('SELECT COUNT(DISTINCT card_name) FROM edhrec_cards')[0][0]}")

# print number of cards total:
print(f"Total Cards: {sql_executer.sql_executer('SELECT COUNT(*) FROM edhrec_cards')[0][0]}")

# print number of unique card_name values with null scryfall_id
print(f"Unique Cards without a scryfall_id: {sql_executer.sql_executer('SELECT COUNT(DISTINCT card_name) FROM edhrec_cards WHERE scryfall_id IS NULL')[0][0]}")

# print number of cards without a scryfall_id
print(f"Cards without a scryfall_id: {sql_executer.sql_executer('SELECT COUNT(*) FROM edhrec_cards WHERE scryfall_id IS NULL')[0][0]}")
