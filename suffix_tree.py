# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from random import choice
import random
import time
seq_dict = {'A': 0, 'T': 1, 'C': 2, 'G': 3}



def gen_seq(len):
    seq = ''
    for i in range(len):
        seq += choice('ATCG')
    return seq
#ref https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf


NUM_CHAR = 5
alphabet = ['A', 'T', 'C', 'G', '$']


class tree_node(object):
    def __init__(self, start_char = 0, end_char = 0):
        self.start_idx = start_char
        self.end_idx = end_char
        self.suffix_link = -1
        self.children ={}
        self.id = -1

    def _print(self):
        print(self.id, self.start_idx, self.end_idx)
        for key, val in self.children.items():
            print(key, val.id)


    def _ref_pair(self):
        edge_end = max(self.start_idx, self.end_idx-1)
        return self.start_idx, edge_end

#
# class tree_suffix(object):
#     def __init__(self, source = 0, start = 0, end = -1):
#         self.source_node = source
#         self.start_char = start
#         self.end_char = end
#
#     def _print(self):
#         print('source node:' + str(self.source_node) + ' start, end: '+str(self.start_char)+' '+str(self.end_char))

        # TODO: canonize - walk down the suffix ???

class suffix_tree(object):
    def __init__(self, text):
        self.text = text+'$'
        self.text_len = len(text)+1
        self.nodes = []
        self.root = tree_node()
        self.root.id = 0
        bot = tree_node(-1, -1)
        bot.id = -1
        self.root.suffix_link = bot

        for char in self.text:
            bot.children[char] = self.root
        self.nodes.append(self.root)
        s = self.root
        k = 0
        for i in range(self.text_len):
            s, k = self._update(s, k, i)
            s, k = self._canonize(s, k, i)
            #print('iteration: '+str(i))
            #self._print()
            #s._print()
            #print(k)

    def _print(self):
        for j in range(len(self.nodes)):
            print('node: ' +str(j))
            self.nodes[j]._print()
    # travel along the suffix to get next node
    def _find_transition(self, s, k):
        # print('find')
        # s._print()
        # print(self.text[k])
        if s.id == -1:
            return self.root
        if self.text[k] in s.children:
            return s.children[self.text[k]]
        return None

    def _find_transition_char(self, s, char):
        if char in s.children:
            return s.children[char]
        return None


    def _canonize(self, s, k, p):
        #print('canonize '+str(k)+' '+str(p))

        if p < k:
            return s, k
        else:
            s_1 = self._find_transition(s, k)
            k_1, p_1 = s_1._ref_pair()
            while p_1 - k_1 <= p - k:
                #p_1, k_1 = s_1._ref_pair()
                k = k + p_1 - k_1 + 1
                s = s_1
                if k <= p:
                    s_1 = self._find_transition(s, k)
                    k_1, p_1 = s_1._ref_pair()
            return s, k


    def _add_child(self, parent_node, start_idx, end_idx):
        child = tree_node(start_idx, end_idx)
        parent_node.children[self.text[start_idx]] = child
        self.nodes.append(child)
        child.id = len(self.nodes)-1
        return child

    def _test_and_split(self, s, k, p, i):
        #print('??')
        #print(s, k, p, i)
        if k <= p:
            s_1 = self._find_transition(s, k)
            k_1, p_1 = s_1._ref_pair()
            split_pos = k_1+p-k+1
            if self.text[i] == self.text[split_pos]:
                return True, s
            else:
                new_child = self._add_child(s, k_1, split_pos)
                s_1.start_idx = split_pos
                new_child.children[self.text[split_pos]] = s_1
                return False, new_child
        else:
            if self.text[i] in s.children:
                return True, s
            else:
                return False, s


    def _update(self, s, k, i):
        oldr = self.root
        end_point, r = self._test_and_split(s, k, i-1, i)
        #new_point = active_point
        while not end_point:
            new_state = self._add_child(r, i, self.text_len)
            if oldr != self.root:
                oldr.suffix_link = r
            oldr = r
            # if s == self.root:
            #     k += 1
            # print('slink')
            # s.suffix_link._print()
            s, k = self._canonize(s.suffix_link, k, i-1)
            end_point, r = self._test_and_split(s, k, i-1, i)
            #active_point._print()
        if oldr != self.root:
            oldr.suffix_link = r
        return s, k

    def search(self, pattern):
        i = 0
        node = self.root
        rem_len = len(pattern)
        t1 = time.time()
        while i < len(pattern):
            next_node = self._find_transition_char(node, pattern[i])
            # no matching outgoing edge
            #next_node._print()
            if next_node == None:
                return -1
            k, p = next_node._ref_pair()
            rem_len = min(p - k+1, len(pattern) - i)
            # doesn't match edge label
            if pattern[i:i+rem_len] != self.text[k:k+rem_len]:
                return -1
            i += p - k + 1
            node = next_node
        #node._print()
        t2 = time.time()
        return node.start_idx - len(pattern) + rem_len, t2-t1

    def search_all(self, patterns):
        for i in range(len(patterns)):
            print(self.search(patterns[i]))


def test(length, patternlen):
    input_text = gen_seq(length)
    # print(input_text)
    search_position = random.randint(0, length-10)
    search_length = random.randint(1, min(length - search_position-1, patternlen))
    search_string = input_text[search_position: search_position+search_length]
    tree = suffix_tree(input_text)
    # print('Searching for pattern:')
    # print(search_string)
    find = tree.search(search_string)
    # print('Found pattern start at position: '+str(find))
    # print(input_text[find:find+search_length])
    if search_string != input_text[find:find+search_length]:
        return -1, search_position, find
    return 0, search_position, find

def test_tree_construction(length):
    input_text = gen_seq(length)
    tree = suffix_tree(input_text)
    print(length)


def test_mem():
    mems = []
    sizes =[]
    from memory_profiler import memory_usage
    #sizes = [50, 100, 200, 500, 1000, 2500, 5000, 10000, 20000, 50000]
    for i in range(1, 50):
        mem_usage =max(memory_usage((test_tree_construction, (i*1000,))))
        #test(sizes[i], 20)
        print(mem_usage)
        sizes.append(i*100)
        mems.append(mem_usage)
    return sizes, mems

def test_const_time():
    times = []
    sizes =[]
    #sizes = [50, 100, 200, 500, 1000, 2500, 5000, 10000, 20000, 50000]
    for i in range(1, 50):
        t1 = time.time()
        test_tree_construction(i*1000)
        t2 = time.time()
        print(t2-t1)
        sizes.append(i*1000)
        times.append(t2-t1)
    return sizes, times

def test_search_time():
    times = []
    sizes =[]
    input_text = gen_seq(20000)
    tree = suffix_tree(input_text)
    #sizes = [50, 100, 200, 500, 1000, 2500, 5000, 10000, 20000, 50000]
    for i in range(1, 100):
        search_position = random.randint(0, 20000 - i * 20)
        search_length = random.randint(1, min(20000 - search_position-1, i*20))
        search_string = input_text[search_position: search_position+search_length]
        print('Searching for pattern:')
        print(search_string)
        t1 = time.time()
        find, t = tree.search(search_string)
        t2 = time.time()
        print('Found pattern start at position: '+str(find))
        print(input_text[find:find+search_length])
        print(t)
        sizes.append(i*100)
        times.append(t2-t1)
    return sizes, times

def test_correctness():
    for i in range(10000):
        length = random.randint(50, 20000)
        patternlen = random.randint(10, max(length/10,15))
        ret, s, f = test(length, patternlen)
        if ret == -1:
            print(s, f)
            print("Wrong!"+str(i))

def test_compare(t_len=5000, p_len=5):
    import ahocorasick
    keywords = []

    for i in range(5):
        kwd = gen_seq(p_len)
        print(kwd)
        keywords.append(kwd)
    text = gen_seq(t_len)
    t1 = time.time()
    tree=ahocorasick.AhoCorasick(keywords)
    t2 = time.time()
    tree.search(text, with_index = True)
    t3 = time.time()
    print(t3-t2, t2-t1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("op")
    args = parser.parse_args()

    if args.op == 'test_mem':
        sizes, mems = test_mem()
        plt.plot(sizes, mems)
        plt.savefig('mem_usage.png')
        plt.clf()
    elif args.op == 'test_const_time':
        sizes, times = test_const_time()
        plt.plot(sizes, times)
        plt.savefig('const_time.png')
        plt.clf()
    elif args.op == 'test_search_time':
        sizes, times = test_search_time()
        plt.plot(sizes, times)
        plt.savefig('search_time.png')
        plt.clf()
    elif args.op == 'test_correctness':
        test_correctness()
    elif args.op == 'test_compare':
        test_compare()
    else:
        print('Yo what do you want')
