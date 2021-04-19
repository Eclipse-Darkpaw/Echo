def get_leftChild(index):
    return 2 * index + 1


def get_rightChild(index):
    return 2 * index + 2


def get_parent(index):
    return (index - 1) // 2


class MaxHeap:
    def __init__(self, lst=[]):
        if len(lst) == 0:
            self.heap = []
        else:
            self.buildheap(lst)

    def extractMax(self):
        if len(self.heap) == 0:
            return RuntimeError('Empty heap')

        value = self.heap[0]

        if len(self.heap) > 1:
            self.heap[0] = self.heap.pop()

        self.sift_down(0)
        return value

    def sift_down(self, index):
        heap = self.heap

        while index < len(heap) // 2:
            left = get_leftChild(index)
            right = get_rightChild(index)

            swap_index, swap_left, swap_right = -1, -1, -1
            if left < len(heap) and heap[index] < heap[left]:
                swap_left = left
            if right < len(heap) and heap[index] < heap[right]:
                swap_right = right

            if swap_left < 0 and swap_right < 0:
                break

            if swap_left > 0 and swap_right > 0:
                if heap[left] > heap[right]:
                    swap_index = left
                else:
                    swap_index = right
            else:
                swap_index = max(swap_left, swap_right)

            heap[index], heap[swap_index] = heap[swap_index], heap[index]
            index = swap_index

    def buildheap(self, lst):
        self.heap = list(lst)
        for i in reversed(range(0, len(lst) // 2)):
            self.sift_down(i)

    def insert(self, value):
        self.heap.append(value)
        index = len(self.heap) - 1
        parent = get_parent(index)
        while index != 0 and self.heap[index] > self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            index, parent = parent, get_parent(parent)

    def __str__(self):
        return str(self.heap)

    def getMax(self):
        return self.heap[0]
