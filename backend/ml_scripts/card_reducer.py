class CardReducer:
    def __init__(self) -> None:
        # Maps to keep track of and the frequency of each card property
        self.seen_effects_triggers = dict()
        self.seen_effects_effects = dict()
        self.seen_abilities_costs = dict()
        self.seen_abilities_effects = dict()
        self.seen_properties = dict()
    
    def reduce_cards(self, cards, min_count=2):
        for card in cards:
            self._see_card(card)
        for card in cards:
            self._reduce_card(card, min_count)
        return cards

    def _see_card(self, card):
        for ability in card['abilities']:
            cost = ability[0]
            effect = ability[1]
            if cost not in self.seen_abilities_costs:
                self.seen_abilities_costs[cost] = 0
            self.seen_abilities_costs[cost] += 1
            if effect not in self.seen_abilities_effects:
                self.seen_abilities_effects[effect] = 0
            self.seen_abilities_effects[effect] += 1
        for effect in card['effects']:
            trigger = effect[0]
            effect = effect[1]
            if trigger not in self.seen_effects_triggers:
                self.seen_effects_triggers[trigger] = 0
            self.seen_effects_triggers[trigger] += 1
            if effect not in self.seen_effects_effects:
                self.seen_effects_effects[effect] = 0
            self.seen_effects_effects[effect] += 1
        for property in card['properties']:
            if property not in self.seen_properties:
                self.seen_properties[property] = 0
            self.seen_properties[property] += 1

    def _reduce_card(self, card, min_count=2):
        # for ability in card['abilities']:
        #     cost = ability[0]
        #     effect = ability[1]
        #     if self.seen_abilities_costs[cost] < min_count:
        #         ability[0] = ""
        #     if self.seen_abilities_effects[effect] < min_count:
        #         ability[1] = ""
        # for effect in card['effects']:
        #     trigger = effect[0]
        #     effect = effect[1]
        #     if self.seen_effects_triggers[trigger] < min_count:
        #         effect[0] = ""
        #     if self.seen_effects_effects[effect] < min_count:
        #         effect[1] = ""
        for property in card['properties']:
            if self.seen_properties[property] < min_count:
                property = ""
        # Flatten the card
        abilities = []
        for property in card['properties']:
            if property != "":
                abilities.append(property)
        return card