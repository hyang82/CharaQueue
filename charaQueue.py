# import sys
import csv
from datetime import datetime
from collections import deque
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

class Student:
    def __init__(self, real, asker_id, was_ans, entered, exited, answered):
        self.real = real
        self.asker_id = asker_id
        self.was_ans = was_ans
        self.entered = entered
        self.exited = exited
        self.answered = answered

    # @classmethod
    # def default(cls):
    #     return cls()

    def __str__(self):
        return "Student id: %s, was_ans: %s" % (self.asker_id, self.was_ans)

def earlierEvent(student1, student2):
    # Returns if student1_event occurs before student2_event. Should compare a datetime.
    if student1 < student2:
        return True
    else:
        return False

def nextEvent(to_enter, next_exit, next_to_ans, next_fin_ans):
    # cur_best is a tuple containing what operation should be done and the current best time.
    # print(to_enter)
    # print(next_exit)
    # print(next_to_ans)
    # print(next_fin_ans)
    # print(next_exit.exited < to_enter.entered)
    # print("done")
    if next_exit.real is True and earlierEvent(next_exit.exited, to_enter.entered):
        cur_best = (2, next_exit.exited)
    else:
        cur_best = (1, to_enter.entered)
    if next_to_ans.real is True and earlierEvent(next_to_ans.answered, cur_best[1]):
        cur_best = (3, next_to_ans.answered)
    if next_fin_ans.real is True and earlierEvent(next_fin_ans.exited, cur_best[1]):
        cur_best = (4, next_fin_ans.exited)
    return cur_best

# CSV file data order
# id, being_answered, topic, created_at, deleted_at, asker_id, answerer_id, lab_queue_id, location, answer_timestamp, course
# Note: Either student is answered or is deleted
def main():
    # input_file = sys.argv[1]
    # input_file = "queue_questions_cs225_feb19.csv"
    input_file = "queue_test.csv"
    data = csv.DictReader(open(input_file))
    will_enter = deque()  # double-ended queue
    for row in data:
        if row["deleted_at"] != "NULL":  # CHANGE THIS -> will omit future data
            real = True
            asker_id = int(row["asker_id"])
            was_ans = bool(int(row["being_answered"]))
            entered = datetime.strptime(row["created_at"], '%m/%d/%Y %H:%M')
            exited = datetime.strptime(row["deleted_at"], '%m/%d/%Y %H:%M')
            if was_ans is True:
                answered = datetime.strptime(row["answer_timestamp"], '%m/%d/%Y %H:%M')
            else:
                answered = datetime.now()
            student = Student(real, asker_id, was_ans, entered, exited, answered)
            #print(student)
            will_enter.append(student)  # Enqueue

    to_exit = Q.PriorityQueue()
    to_be_ans = Q.PriorityQueue()
    answering = Q.PriorityQueue()
    counter = 0
    #print(datetime.now())
    #print(datetime.now())

    while will_enter:  # Checks deque as boolean (no empty() function)
        counter += 1
        #print(counter)
        to_enter = will_enter[0]
        if not to_exit.empty():
            next_exit = (to_exit.queue[0])[1]  # Must access tuple
        else:
            next_exit = Student(False, 0, False, datetime.now(), datetime.now(), datetime.now())
        if not to_be_ans.empty():
            next_to_ans = (to_be_ans.queue[0])[1]
        else:
            next_to_ans = Student(False, 0, False, datetime.now(), datetime.now(), datetime.now())
        if not answering.empty():
            next_fin_ans = (answering.queue[0])[1]
        else:
            next_fin_ans = Student(False, 0, False, datetime.now(), datetime.now(), datetime.now())

        # Determine where event should go based on the return value from the nextEvent function.
        # print(next_exit)
        # print("to_enter: " + str(to_enter))
        # print("next_exit: " + str(next_exit))
        # print("next_to_ans: " + str(next_to_ans))
        # print("next_fin_ans: " + str(next_fin_ans))
        nextev = nextEvent(to_enter, next_exit, next_to_ans, next_fin_ans)
        print(nextev)
        if nextev[0] is 1:
            if to_enter.was_ans is True:
                # if not to_be_ans.empty():
                #     testing = (to_be_ans.queue[0])[1]
                #     print(to_enter.answered > testing.answered)
                #     print(testing.answered)
                #     print(to_enter.answered)
                #     print("here")
                to_be_ans.put((to_enter.answered, to_enter))  # Place into to_be_ans queue.
                will_enter.popleft()
            else:
                to_exit.put((to_enter.exited, to_enter))  # Place into to_exit queue (i.e. left early).
                will_enter.popleft()
        elif nextev[0] is 2:
            to_exit.get()  # Dequeue from the exit queue
        elif nextev[0] is 3:
            answering.put((next_to_ans.answered, next_to_ans))  # Place into answering queue.
            to_be_ans.get()  # Dequeue from the waiting-to-be-answered queue
        else:
            answering.get()  # Dequeue - Finished answering

    print("done")

# Must modify the CSV file. Check when the answerer (TA/CA) ID starts to answer another person and then update the exit
# time of the previous person.
main()
