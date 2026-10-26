from decimal import Decimal, InvalidOperation

def expense_totals(expenses, members):
    # Calculate in cents
    people = {}
    for member in members:
        people[member.userId] = {"name": member.user.username, "paid": 0, "share": 0}
    total = 0
    for expense in expenses:
        cents = int(expense.amount * 100)
        total += cents
        people.setdefault(expense.paidByUserId, {"name": expense.paid_by_user.username, "paid": 0, "share": 0})
        people[expense.paidByUserId]["paid"] += cents
        splits = {split.userId: split.user for split in expense.splits}
        if not splits:
            raise ValueError("An existing expense has no participants. Ask a campmaster to remove and recreate it.")
        share, remainder = divmod(cents, len(splits))
        for index, user_id in enumerate(sorted(splits)):
            people.setdefault(user_id, {"name": splits[user_id].username, "paid": 0, "share": 0})
            people[user_id]["share"] += share
            if index < remainder:
                people[user_id]["share"] += 1
    for person in people.values():
        person["balance"] = person["share"] - person["paid"]
    return total, people
