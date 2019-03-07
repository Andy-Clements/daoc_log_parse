import sys, re
import argparse

total_damage = 0

MeleeCombat = False
CasterCombat = False
Mainhand = False
Crit = False
Defense = False
LootMoney = False


def parse_money(openFile):
    """Counts the amount of money paid and received"""
    money_spent = 0
    money_gained = 0
    lines = openFile.readlines()
    for line in lines:
        if line.find('gives you') != -1:
            money_gained = currency_to_copper(line)
        elif line.find('You just bought') != -1:
            money_spent = currency_to_copper(line)
    print_currency("Money gained: ", money_gained)
    print_currency("Money spent: ", money_spent)
    if money_gained > money_spent:
        print_currency("Net income: ", copper_to_currency(money_gained - money_spent))
    else:
        print_currency("Net loss: ", copper_to_currency(money_spent-money_gained))

def parse_gold_loot(openFile):
    """Counts amount of gold picked up from mobs"""
    money_looted = 0
    for line in openFile:
        if line.find('You pick up') != -1 or line.find('for this kill') != -1:
            money_looted += currency_to_copper(line)
    print_currency("Loot money: ", copper_to_currency(money_looted))

def copper_to_currency(total):
    """Helper method to parse_money. Seperates 'total' into largest denominations
       and returns the results a dictionary"""
    print(total)
    result = {}
    try:
        result['plat'] = str(int(total)/10000000)
        result['gold'] = str(int((total%10000000)/10000))
        result['silver'] = str(int((total%10000)/100))
        result['copper'] = str(int(total%100))
    except TypeError:
        result=total

    return result

## Helper method to parse currency amount from line and return it in copper denomination
def currency_to_copper(line):
    """Helper method to parse currency amount from line and return it in copper denomination"""
    total_currency_amount = 0
    if line.find('plat') != -1:
        plat_text = line[line.find('plat')-4:line.find('plat')]
        total_currency_amount += 10000000 * int(plat_text.split()[len(plat_text.split())-1])
    if line.find('gold') != -1:
        gold_text = line[line.find('gold')-4:line.find('gold')]
        total_currency_amount += 10000 * int(gold_text.split()[len(gold_text.split())-1])
    if line.find('silver') != -1:
        total_currency_amount += 100 * int(line[line.find('silver')-3:line.find('silver')-1])
    if line.find('copper') != -1:
        total_currency_amount += int(line[line.find('copper')-3:line.find('copper')-1])
    return total_currency_amount

def print_currency(preamble, currency_in_copper):
    """Converts currency_in_copper to the largest denominations,
       and prints out the reader-friendly amounts"""
    print(preamble)
    denominated_currency = copper_to_currency(currency_in_copper)
    print(denominated_currency['plat'] + 'p ' +
          denominated_currency['gold'] + 'g ' +
          denominated_currency['silver'] + 's ' +
          denominated_currency['copper'] + 'c')

## Counts and returns the # of successful attacks with both hands
def parse_melee_combat(openFile):
    """Counts and returns the # of successful attacks with both hands and total damage"""
    try:
        hit_count = 0
        total_damage = 0
        for line in openFile:
            if line.find('You attack') != -1 and line.find('with your') != -1:
                hit_count += 1
                #damage_text = line[line.find('damage')-16:line.find('damage')]
                total_damage += int(re.search('( [0-9]+)', line)[0])
                '''if line.find('-') != -1 or line.find('+') != -1 and '(' in line:
                    try:
                        total_damage += int(damage_text.split()[len(damage_text.split())-2])
                    except ValueError:
                        print("Value Error: {} @ linesplit-2".format(damage_text))
                else:
                    total_damage += int(damage_text.split()[len(damage_text.split())-1])'''
        print("# of melee hits: " + str(hit_count))
        print('     Total damage dealt: ' + str(total_damage))
        return hit_count
    except IndexError:
        print(str(line))
        exit(0)

def parse_caster_combat(openFile):
    """Counts and returns the # of successful damage spells and total damage"""
    try:
        hit_count = 0
        resist_count = 0
        total_damage = 0
        for line in openFile:
            if line.find('You hit') != -1:
                hit_count += 1
                damage_text = line[line.find('damage')-16:line.find('damage')]
                if line.find('-') != -1 or line.find('+') != -1:
                    total_damage += int(damage_text.split()[len(damage_text.split())-2])
                else:
                    total_damage += int(damage_text.split()[len(damage_text.split())-1])
            if line.find('resists the effect') != -1:
                resist_count += 1
        print("# nukes landed: " + str(hit_count))
        print("     Total damage: " + str(total_damage))
        print("# nukes resisted: " + str(resist_count) + "\n")
        return hit_count
    except IndexError:
        print(str(line))
        exit(0)

## Counts and returns the # of critical hits inflicted with either hand.
def parse_crit(openFile):
    crit_count = 0
    for line in openFile:
        if line.find('You critical hit') != -1:
            crit_count += 1
    print("# of crits: " + str(crit_count))
    return crit_count

## Counts # of attacks made with user-input 'weaponName'.
def parse_mainhand(openFile, weaponName):
    mainhand_count = 0
    print(weaponName)
    for line in openFile:
        if line.find('with your ' + weaponName) != -1:
            mainhand_count += 1
    print("# of mainhand hits: " + str(mainhand_count))

def parse_defense(openFile):
    """Counts # blocks, # misses, # parries, # evades, # hits taken.
       Prints results, along with %'s."""
    block_count = 0
    parry_count = 0
    evade_count = 0
    hits_taken = 0
    total_damage = 0
    misses = 0
    try:
        for line in openFile:
            if line.find('you block the blow') != -1:
                block_count += 1
            elif line.find('you parry the blow') != -1:
                parry_count += 1
            elif line.find('you evade the blow') != -1:
                evade_count += 1
            elif line.find('hits your') != -1:
                hits_taken += 1
                damage_text = line[line.find('damage')-9:line.find('damage')]
                if line.find('-') != -1 or line.find('+') != -1:
                    total_damage += int(damage_text.split()[len(damage_text.split())-2])
                else:
                    total_damage += int(damage_text.split()[len(damage_text.split())-1])
            elif line.find('attacks you and misses') != -1:
                misses += 1
            total_attacks = block_count + parry_count + evade_count + hits_taken + misses
        print("Defensive statistics:\n")
        print("Total attacks received: " + str(total_attacks))
        if total_attacks != 0:
            print("Block count: " + str(block_count) +
                  "\n\tBlock %: " + str((float(block_count))/(float(total_attacks))) +
                  "\nParry count: " + str(parry_count) +
                  "\n\tParry %: " + str((float(parry_count))/(float(total_attacks))) +
                  "\nEvade Count " + str(evade_count) +
                  "\n\tEvade %: " + str((float(evade_count))/(float(total_attacks))) +
                  "\nMiss count: " + str(misses) +
                  "\n\tMiss %: " + str((float(misses))/(float(total_attacks))) +
                  "\nHits taken: " + str(hits_taken) +
                  "\n\tHit %: " + str((float(hits_taken))/(float(total_attacks))) +
                  "\nTotal damage taken: " + str(total_damage) + "\n")
    except ValueError or IndexError:
        print(line)
        exit(0)

## Executes parse_combat, parse_crit, and parse_defense.
def parse_allCombat(openFile):
    """Executes parse_combat, parse_crit, and parse_defense."""
    hit_count = parse_melee_combat(openFile)
    openFile.seek(0)
    spell_count = parse_caster_combat(openFile)
    openFile.seek(0)
    crit_count = parse_crit(openFile)
    try:
        print("Crit %: " + str(float(crit_count)/float(hit_count + spell_count)) + "\n")
    except ZeroDivisionError:
        print("Crit %: Divided by 0" + str(float(crit_count)) + "\n")
    openFile.seek(0)
    parse_defense(openFile)

## Executes parse_money and parse_gold_loot.
def parse_allMoney(openFile):
    """Executes parse_money and parse_gold_loot."""
    parse_money(openFile)
    print("\n")
    openFile.seek(0)
    parse_gold_loot(openFile)

## Executes parse_allCombat and parse_allMoney.
"""Executes parse_allCombat and parse_allMoney."""
def parse_all(openFile):
    print("Combat statistics:\n")
    parse_allCombat(openFile)
    openFile.seek(0)
    print("Financial statistics: ")
    parse_allMoney(openFile)


def main():
    parser = argparse.ArgumentParser(description="Super awesome DAOC chatlog parser.")

    # Path to chat.log
    parser.add_argument('-p', nargs=1, action="store", dest="in_path")

    # Commands
    parser.add_argument('-mc', '--meleeCombat', action="store_true")
    parser.add_argument('-cc', '--casterCombat', action="store_true")
    parser.add_argument('-mh', '--Mainhand', nargs=1)
    parser.add_argument('-c', '--Crit', action="store_true")
    parser.add_argument('-d', '--Defense', action="store_true")
    parser.add_argument('-ac', '--allCombat', action="store_true")
    parser.add_argument('-mo', '--Money', action="store_true")
    parser.add_argument('-lm', '--lootMoney', action="store_true")
    parser.add_argument('-am', '--allMoney', action="store_true")
    parser.add_argument('-a', '--All', action="store_true")

    args = parser.parse_args()

    try:
        if not args.in_path:
            in_path = 'C:\\Users\\Draqolv\\Documents\\Electronic Arts\\Dark Age of Camelot\\chat.log'
        else:
            in_path = args.in_path[0]

        with open(in_path, 'r') as readf:
            if args.meleeCombat:
                parse_melee_combat(readf)
            if args.casterCombat:
                parse_caster_combat(readf)
            if args.Mainhand:
                parse_mainhand(readf, args.Mainhand[0])
            if args.Crit:
                parse_crit(readf)
            if args.Defense:
                parse_defense(readf)
            if args.allCombat:
                parse_allCombat(readf)
            if args.Money:
                parse_money(readf)
            if args.lootMoney:
                parse_gold_loot(readf)
            if args.allMoney:
                parse_allMoney(readf)
            if args.All:
                parse_all(readf)

    except IOError:
        print("Failed to open " + args.in_path)


main()
