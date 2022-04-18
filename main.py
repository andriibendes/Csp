import numpy as np
import time
import random
from tabulate import tabulate

week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

g_names = ["TK", "TTP", "MI"]

s_names = ["Algebra", "Math Anal.", "Geometry", "Programming", "Discrete Math",
           "Algorithms", "Data Str.", "Prob. Th.", "Data Analysis", "Num. Math."]

t_names = ["Alex", "John", "David", "Matt", "Sam", "Allan", "Antony", "Peter", "Todd", "Bart"]


class Schedule:
    n_days = 5
    n_lessons = 4
    total_lessons = n_days * n_lessons

    n_teachers = 4
    n_groups = 3
    n_rooms = 5
    n_subjects = 6

    n_s_per_t = 4  # number of subjects per teacher
    n_s_per_g = 3  # number of subjects per group

    def __init__(self):
        self.rooms = [f"R{i}" for i in range(1, self.n_rooms + 1)]
        self.groups = g_names[:self.n_groups]
        self.subjects = s_names[:self.n_subjects]
        self.teachers = t_names[:self.n_teachers]

        self.rooms_dests = ["lec"] * self.n_rooms
        for i in range(0, self.n_rooms, 2):
            self.rooms_dests[i] = "lab"

        # subjects teacher cat teach
        self.teacher_specs = [set([(si ** 2 + ti ** 2) % self.n_subjects for si in range(self.n_s_per_t)])
                              for ti in range(self.n_teachers)]

        # subjects group is being taught
        self.learning_plan = [set([(si ** 2 + gi) % self.n_subjects for si in range(self.n_s_per_g)])
                              for gi in range(self.n_groups)]

        # room per lesson per group
        self.rpl = [[None] * self.n_groups for _ in range(self.total_lessons)]

        # subject per lesson per group
        self.spl = [[None] * self.n_groups for _ in range(self.total_lessons)]

        # teacher per lesson per group
        self.tpl = [[None] * self.n_groups for _ in range(self.total_lessons)]

        self.cnt = 0

    def is_complete(self):
        return all([not any(lg is None for lg in l) for l in self.rpl])

    def check_constraints(self):
        self.cnt += 1
        # if self.cnt == 1e6:
        #     return True
        # classes are complete if only they have both labs and lectures
        if self.is_complete():
            for g in range(self.n_groups):
                class_types_per_subjects = {s: set() for s in self.learning_plan[g]}
                for l in range(self.total_lessons):
                    class_types_per_subjects[self.spl[l][g]].add(self.rooms_dests[self.rpl[l][g]])
                if any([len(s) != 2 for s in class_types_per_subjects.values()]):
                    return False

        # each teacher can teach only 1 group at a time
        for tpg in self.tpl:
            for i in range(self.n_groups - 1):
                if tpg[i] is not None and tpg[i] in tpg[i + 1:]:
                    return False

        # each room can be used only by 1 group at a time
        for rpg in self.rpl:
            for i in range(self.n_groups - 1):
                if rpg[i] is not None and rpg[i] in rpg[i + 1:]:
                    return False

        # each teacher can only teach its classes
        # each group can have only its classes taught
        # commented this part because it is specified in the backtracking method

        # each group can only visit 1 class at a time
        # this constraint is maintained by the code structure ! :)

        return True

    def setter(self, l, g, t, r, s):
        self.tpl[l][g] = t
        self.rpl[l][g] = r
        self.spl[l][g] = s



    def degree_heuristic(self):
        none_list = []
        for l in range(self.total_lessons):
            none_list.append(sum([self.tpl[l][g] is None for g in range(self.n_groups)]))
        l = none_list.index(max(none_list))
        for g in range(self.n_groups):
            if self.tpl[l][g] is None:
                return l, g

    def mrv(self):
        for d in range(self.n_days):
            for l in range(self.n_lessons):
                l = d * self.n_lessons + l
                for g in range(self.n_groups):
                    if self.tpl[l][g] is None:
                        return l, g

    def order_domain_vals(self, g):
        for t in random.sample(range(self.n_teachers), self.n_teachers):
            available_subjects = list(self.learning_plan[g].intersection(self.teacher_specs[t]))
            for r in random.sample(range(self.n_rooms), self.n_rooms):
                for s in random.sample(available_subjects, len(available_subjects)):
                    yield t, r, s

    def lcv(self, g):
        teacher_scores = []
        for t in range(self.n_teachers):
            teacher_scores.append([0, t])
            for gi in range(self.n_groups):
                if gi != g:
                    teacher_scores[-1][0] += len(self.teacher_specs[t].intersection(self.learning_plan[gi]))
        for _, t in sorted(teacher_scores, key=lambda sc: sc[0]):
            available_subjects = list(self.learning_plan[g].intersection(self.teacher_specs[t]))
            for r in random.sample(range(self.n_rooms), self.n_rooms):
                for s in random.sample(available_subjects, len(available_subjects)):
                    yield t, r, s

    def forward_check(self, l, g):
        for t in random.sample(range(self.n_teachers), self.n_teachers):
            if t not in self.tpl[l]:
                available_subjects = list(self.learning_plan[g].intersection(self.teacher_specs[t]))
                for r in random.sample(range(self.n_rooms), self.n_rooms):
                    if r not in self.rpl[l]:
                        for s in random.sample(available_subjects, len(available_subjects)):
                            yield t, r, s


    def backtracking(self):
        var = self.mrv()  # self.degree_heuristic()

        if var is None:
            return True

        l, g = var

        for t, r, s in self.order_domain_vals(g):  # self.forward_check(l, g): # self.lcv(g):
            self.setter(l, g, t, r, s)

            if self.check_constraints():
                res = self.backtracking()
                if res:
                    return True
            self.setter(l, g, None, None, None)
        return False

    def print(self):
        table = dict(indices=["Day", "Group"] + list(range(1, self.n_lessons + 1)))
        for d in range(self.n_days):
            table[(d, 0)] = [week_days[d]]
            for g in range(1, self.n_groups):
                table[(d, g)] = [""]
            for g in range(self.n_groups):
                table[(d, g)].append(g_names[g])
                for l in range(self.n_lessons):
                    l = d * self.n_lessons + l
                    lesson = (f"{self.subjects[self.spl[l][g]]}\n"
                              f"({self.rooms_dests[self.rpl[l][g]]})\n"
                              f"Room: {self.rooms[self.rpl[l][g]]}\n"
                              f"Prof.: {self.teachers[self.tpl[l][g]]}")
                    table[(d, g)].append(lesson)
            table[(d, -1)] = [""] * (2 + self.n_lessons)
        print(tabulate(table, tablefmt="fancy_grid"))



csp = Schedule()

print("Start!")
start = time.time()
csp.backtracking()
print(f"Success! Time spent: {time.time() - start} s.")
print(f"Constraints checked {csp.cnt} times!")
csp.print()
