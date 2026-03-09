#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <vector>

using namespace std;

// ================= ITERATION COUNTERS =================
long long iterMerge = 0;
long long iterQuick = 0;
long long iterHeap = 0;
long long iterShell = 0;

// ================= DISPLAY =================
void printArray(const vector<int>& arr) {
    for (int x : arr) {
        cout << x << " ";
    }
    cout << endl;
}

// ================= MERGE SORT =================
void mergeArray(vector<int>& arr, int left, int mid, int right) {
    vector<int> L(arr.begin() + left, arr.begin() + mid + 1);
    vector<int> R(arr.begin() + mid + 1, arr.begin() + right + 1);

    int i = 0, j = 0, k = left;

    while (i < (int)L.size() && j < (int)R.size()) {
        iterMerge++;
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }

    while (i < (int)L.size()) {
        arr[k++] = L[i++];
    }

    while (j < (int)R.size()) {
        arr[k++] = R[j++];
    }
}

void mergeSort(vector<int>& arr, int left, int right) {
    if (left >= right) return;

    iterMerge++;
    int mid = left + (right - left) / 2;

    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);
    mergeArray(arr, left, mid, right);
}

// ================= QUICK SORT =================
int partitionArray(vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        iterQuick++;
        if (arr[j] <= pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }

    swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quickSort(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partitionArray(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

// ================= HEAP SORT =================
void heapify(vector<int>& arr, int n, int i) {
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n) {
        iterHeap++;
        if (arr[left] > arr[largest]) {
            largest = left;
        }
    }

    if (right < n) {
        iterHeap++;
        if (arr[right] > arr[largest]) {
            largest = right;
        }
    }

    if (largest != i) {
        swap(arr[i], arr[largest]);
        heapify(arr, n, largest);
    }
}

void heapSort(vector<int>& arr) {
    int n = arr.size();

    for (int i = n / 2 - 1; i >= 0; i--) {
        heapify(arr, n, i);
    }

    for (int i = n - 1; i > 0; i--) {
        swap(arr[0], arr[i]);
        heapify(arr, i, 0);
    }
}

// ================= SHELL SORT =================
void shellSort(vector<int>& arr) {
    int n = arr.size();

    for (int gap = n / 2; gap > 0; gap /= 2) {
        for (int i = gap; i < n; i++) {
            int temp = arr[i];
            int j = i;

            while (j >= gap) {
                iterShell++;
                if (arr[j - gap] > temp) {
                    arr[j] = arr[j - gap];
                    j -= gap;
                } else {
                    break;
                }
            }

            arr[j] = temp;
        }
    }
}

// ================= MAIN =================
int main() {
    int n, choice;

    cout << "Enter number of elements: ";
    cin >> n;

    vector<int> arr(n);

    cout << "Choose input method:\n";
    cout << "1. Manual input\n";
    cout << "2. Random values\n";
    cout << "Your choice: ";
    int inputChoice;
    cin >> inputChoice;

    if (inputChoice == 1) {
        cout << "Enter the elements:\n";
        for (int i = 0; i < n; i++) {
            cin >> arr[i];
        }
    } else {
        srand((unsigned)time(0));
        for (int i = 0; i < n; i++) {
            arr[i] = rand() % 1000;
        }
        cout << "Generated array:\n";
        printArray(arr);
    }

    cout << "\nChoose sorting algorithm:\n";
    cout << "1. Merge Sort\n";
    cout << "2. Quick Sort\n";
    cout << "3. Heap Sort\n";
    cout << "4. Shell Sort\n";
    cout << "5. All (run all algorithms)\n";
    cout << "Your choice: ";
    cin >> choice;

    auto resetIterations = [&]() {
        iterMerge = iterQuick = iterHeap = iterShell = 0;
    };

    switch (choice) {
        case 1:
            resetIterations();
            mergeSort(arr, 0, n - 1);
            cout << "\nSorted with Merge Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterMerge << endl;
            break;

        case 2:
            resetIterations();
            quickSort(arr, 0, n - 1);
            cout << "\nSorted with Quick Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterQuick << endl;
            break;

        case 3:
            resetIterations();
            heapSort(arr);
            cout << "\nSorted with Heap Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterHeap << endl;
            break;

        case 4:
            resetIterations();
            shellSort(arr);
            cout << "\nSorted with Shell Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterShell << endl;
            break;

        case 5: {
            vector<int> original = arr;

            cout << "\nOriginal array:\n";
            printArray(original);

            resetIterations();
            arr = original;
            mergeSort(arr, 0, n - 1);
            cout << "\nSorted with Merge Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterMerge << endl;

            resetIterations();
            arr = original;
            quickSort(arr, 0, n - 1);
            cout << "\nSorted with Quick Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterQuick << endl;

            resetIterations();
            arr = original;
            heapSort(arr);
            cout << "\nSorted with Heap Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterHeap << endl;

            resetIterations();
            arr = original;
            shellSort(arr);
            cout << "\nSorted with Shell Sort:\n";
            printArray(arr);
            cout << "Iterations: " << iterShell << endl;

            break;
        }

        default:
            cout << "Invalid choice!\n";
    }

    return 0;
}