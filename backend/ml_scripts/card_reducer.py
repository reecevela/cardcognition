import json
class CardReducer:
    def __init__(self) -> None:
        # Maps to keep track of and the frequency of each card property
        self.seen_effects_triggers = dict()
        self.seen_effects_effects = dict()
        self.seen_abilities_costs = dict()
        self.seen_abilities_effects = dict()
        self.seen_properties = dict()
        self.seen_subtypes = dict()
    
    def reduce_cards(self, cards, min_count=2):
        for card in cards:
            self._see_card(card)
        for card in cards:
            self._reduce_card(card, min_count)
        return cards

    def _see_card(self, card):
        try: 
            for ability in card['abilities']:
                cost = str(ability[0])
                effect = str(ability[1])
                if self.seen_abilities_costs.get(cost) is None:
                    self.seen_abilities_costs[cost] = 0
                self.seen_abilities_costs[cost] += 1
                if self.seen_abilities_effects.get(effect) is None:
                    self.seen_abilities_effects[effect] = 0
                self.seen_abilities_effects[effect] += 1
                if 'SUB_' in cost:
                    subtype = cost.split('SUB_')[1]
                    if self.seen_subtypes.get(subtype) is None:
                        self.seen_subtypes[subtype] = 0
                    self.seen_subtypes[subtype] += 1
                if 'SUB_' in effect:
                    subtype = effect.split('SUB_')[1]
                    if self.seen_subtypes.get(subtype) is None:
                        self.seen_subtypes[subtype] = 0
                    self.seen_subtypes[subtype] += 1
            for effect in card['effects']:
                trigger = str(effect[0])
                effect = str(effect[1])
                if self.seen_effects_triggers.get(trigger) is None:
                    self.seen_effects_triggers[trigger] = 0
                self.seen_effects_triggers[trigger] += 1
                if self.seen_effects_effects.get(effect) is None:
                    self.seen_effects_effects[effect] = 0
                self.seen_effects_effects[effect] += 1
                if 'SUB_' in trigger:
                    subtype = trigger.split('SUB_')[1]
                    if self.seen_subtypes.get(subtype) is None:
                        self.seen_subtypes[subtype] = 0
                    self.seen_subtypes[subtype] += 1
                if 'SUB_' in effect:
                    subtype = effect.split('SUB_')[1]
                    if self.seen_subtypes.get(subtype) is None:
                        self.seen_subtypes[subtype] = 0
                    self.seen_subtypes[subtype] += 1
            for property in card['properties']:
                if self.seen_properties.get(property) is None:
                    self.seen_properties[property] = 0
                self.seen_properties[property] += 1
        except Exception as e:
            # print(card)
            # print(e)
            pass

    def _reduce_card(self, card, min_count=2):
        return card
        # Filter subtype out if not mentioned min_count times in effects, triggers, or abilities etc
        # Subtypes start with SUB_
        subtypes = [prop for prop in card['properties'] if prop.startswith('SUB_')]
        subtypes = [subtype for subtype in subtypes if subtype in self.seen_subtypes and self.seen_subtypes[subtype] >= min_count]
        filtered_properties = [prop for prop in card['properties'] if self.seen_properties[prop] >= min_count]
        card['properties'] = filtered_properties
        return card