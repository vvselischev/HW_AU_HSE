package ru.hsespb;

import guru.nidi.graphviz.engine.Format;
import guru.nidi.graphviz.engine.Graphviz;
import guru.nidi.graphviz.model.Graph;
import static guru.nidi.graphviz.model.Factory.*;
import guru.nidi.graphviz.attribute.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Paths;
import java.util.*;

public class Main {

    class Pair<S, T> {
		public S first;
		public T second;

		public Pair(S first, T second) {
			this.first = first;
			this.second = second;
		}
	}

    class Automata {
        public Automata(int size, int startNode) {
            finishNodes = new HashSet<>();
            alphabet = new HashSet<>();
            adjacent = new ArrayList<>();
            this.size = size;
            this.startNode = startNode;
        }

        public Automata(int size, int startNode, Set<Integer> finishNodes, Set<Character> alphabet,
                        List<HashMap<Character, Integer>> adjacent) {
            this.size = size;
            this.startNode = startNode;
            this.finishNodes = finishNodes;
            this.alphabet = alphabet;
            this.adjacent = adjacent;
        }

        public HashMap<Character, Integer> getAdjacent(int node) {
            return adjacent.get(node);
        }

        public Set<Integer> getFinishNodes() {
            return finishNodes;
        }

        public Set<Character> getAlphabet() {
            return alphabet;
        }

        public List<HashMap<Character, Integer>> getAdjacentList() {
            return adjacent;
        }

        public int getSize() {
            return size;
        }

        public int getStartNode() {
            return startNode;
        }

        private int size;
        private int startNode;
        private Set<Integer> finishNodes;
        private Set<Character> alphabet;
        private List<HashMap<Character, Integer>> adjacent;
    }

    void Solve() throws IOException {
        Scanner console = new Scanner(System.in);
        Scanner scanner = new Scanner(Paths.get(console.nextLine()));

        Map<Integer, Map<Character, List<Integer>>> invertEdges = new HashMap<>();
        Automata inputAutomata = readAutomata(scanner, invertEdges);

        printAutomataGraph(inputAutomata, "output/input.png");

        Automata outputAutomata = minimizeAutomata(inputAutomata, invertEdges);

        printAutomataGraph(outputAutomata, "output/output.png");
        printAutomataText(outputAutomata, "output/output.txt");

        //testAll();
    }

    private Automata minimizeAutomata(Automata inputAutomata, Map<Integer, Map<Character, List<Integer>>> invertEdges)
            throws FileNotFoundException {
        markReachable(inputAutomata);

        Queue<Pair<Integer, Integer>> queue = new LinkedList<>();
        boolean[][] marked = new boolean[inputAutomata.getSize()][inputAutomata.getSize()];
        List<Set<Integer>> outputNodes = new ArrayList<>();
        int[] component = new int[inputAutomata.getSize()];

        initDifferentiatedNodes(inputAutomata, queue, marked);
        fillDifferentiatedTable(inputAutomata.getAlphabet(), invertEdges, queue, marked);
        fillEquivalenceComponents(inputAutomata.getSize(), marked, outputNodes, component);

        return getOutputAutomata(inputAutomata, outputNodes, component);
    }

    public static void main(String[] args) {
        try {
            new Main().Solve();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void printAutomataText(Automata automata, String name) throws FileNotFoundException {
        PrintWriter writer = new PrintWriter(name);
        writer.print(automata.getSize());
        writer.print(' ');
        writer.print(automata.getStartNode());
        writer.print(' ');
        writer.print(automata.getFinishNodes().size());
        writer.print(' ');
        writer.println(automata.getAlphabet().size());

        for (int i = 0; i < automata.getSize(); i++) {
	        writer.println();
            for (char c : automata.getAdjacent(i).keySet()) {
                writer.print(c);
                writer.print(' ');
                writer.println(automata.getAdjacent(i).get(c));
            }
        }

        for (int finish : automata.getFinishNodes()) {
            writer.print(finish);
            writer.print(' ');
        }
        writer.close();
    }

    private void printAutomataGraph(Automata automata, String name) throws IOException {
        Graph g = graph().directed().graphAttr().with(RankDir.LEFT_TO_RIGHT);
        for (int i = 0; i < automata.getSize(); i++) {
            if (automata.getFinishNodes().contains(i)) {
                g = g.with(node("" + i).with(Label.of(""), Shape.DOUBLE_CIRCLE));
            }
            else {
                g = g.with(node("" + i).with(Label.of("")));
            }
        }

        for (int i = 0; i < automata.getSize(); i++) {
            for (char c : automata.getAdjacent(i).keySet()) {
                g = g.with(node("" + i).link(to(node("" + automata.getAdjacent(i).get(c))).with(Label.of("" + c))));
            }
        }

        g = g.with(node("fictive start").with(Style.INVIS).link(to(node("" + automata.getStartNode()))));
        Graphviz.fromGraph(g).width(900).render(Format.PNG).toFile(new File(name));
    }

    private Automata getOutputAutomata(Automata inputAutomata, List<Set<Integer>> outputNodes, int[] component) {
        Set<Integer> outputFinishNodes = new HashSet<>();
        List<HashMap<Character, Integer>> outputAutomataList = new ArrayList<>();
        Set<Character> outputAlphabet = new HashSet<>();
        int outputStartNode = 0;
        for (int i = 0; i < outputNodes.size(); i++) {
            outputAutomataList.add(new HashMap<>());
            for (int oldNode : outputNodes.get(i)) {
                if (inputAutomata.getFinishNodes().contains(oldNode)) {
                    outputFinishNodes.add(i);
                }
                if (oldNode == inputAutomata.getStartNode()) {
                    outputStartNode = component[oldNode];
                }
                for (char adj : inputAutomata.getAdjacentList().get(oldNode).keySet()) {
                    int adjacentNode = inputAutomata.getAdjacentList().get(oldNode).get(adj);
                    outputAutomataList.get(i).put(adj, component[adjacentNode]);
                    outputAlphabet.add(adj);
                }
            }
        }
        return new Automata(outputAutomataList.size(), outputStartNode, outputFinishNodes,
                outputAlphabet, outputAutomataList);
    }

    private void fillEquivalenceComponents(int n, boolean[][] marked, List<Set<Integer>> outputNodes, int[] component) {
        boolean[] used = new boolean[n];
        for (int i = 0; i < n; i++) {
            if (!reachable[i]) {
                continue;
            }
            if (!used[i]) {
                used[i] = true;
                outputNodes.add(new HashSet<>());
                int currentComponentId = outputNodes.size() - 1;
                outputNodes.get(currentComponentId).add(i);
                component[i] = currentComponentId;
                for (int j = i + 1; j < n; j++) {
                    if (reachable[j] && !used[j] && !marked[i][j]) {
                        used[j] = true;
                        outputNodes.get(outputNodes.size() - 1).add(j);
                        component[j] = currentComponentId;
                    }
                }
            }
        }
    }

    private void fillDifferentiatedTable(Set<Character> alphabet,
                                         Map<Integer, Map<Character, List<Integer>>> invertEdges,
                                         Queue<Pair<Integer, Integer>> queue, boolean[][] marked) {
        while (!queue.isEmpty()) {
            Pair<Integer, Integer> current = queue.poll();
            if (!reachable[current.first] || !reachable[current.second]) {
                continue;
            }

            for (char c : alphabet) {
                if (!invertEdges.containsKey(current.first) ||
                        !invertEdges.get(current.first).containsKey(c) ||
                        !invertEdges.containsKey(current.second)) {
                    continue;
                }

                for (int firstPrevious : invertEdges.get(current.first).get(c)) {
                    if (!reachable[firstPrevious] || !invertEdges.get(current.second).containsKey(c)) {
                        continue;
                    }
                    for (int secondPrevious : invertEdges.get(current.second).get(c)) {
                        if (!marked[firstPrevious][secondPrevious] && reachable[secondPrevious]) {
                            marked[firstPrevious][secondPrevious] = true;
                            marked[secondPrevious][firstPrevious] = true;
                            queue.add(new Pair<>(firstPrevious, secondPrevious));
                        }
                    }
                }
            }
        }
    }

    private Automata readAutomata(Scanner scanner, Map<Integer, Map<Character, List<Integer>>> invertEdges) {
        int size = scanner.nextInt();
        int start = scanner.nextInt();
        Automata automata = new Automata(size, start);
        int finishCount = scanner.nextInt();
	int alphabetSize = scanner.nextInt();
        for (int i = 0; i < automata.getSize(); i++) {
            automata.getAdjacentList().add(new HashMap<>());
            for (int j = 0; j < alphabetSize; j++) {
		scanner.nextLine();
                char c = scanner.next().charAt(0);
                int next = scanner.nextInt();
                automata.getAdjacentList().get(i).put(c, next);
                automata.getAlphabet().add(c);
                if (!invertEdges.containsKey(next)) {
                    invertEdges.put(next, new HashMap<>());
                }
                if (!invertEdges.get(next).containsKey(c)) {
                    invertEdges.get(next).put(c, new ArrayList<>());
                }
                invertEdges.get(next).get(c).add(i);
            }
        }
        if (!invertEdges.containsKey(automata.getStartNode())) {
            invertEdges.put(automata.getStartNode(), new HashMap<>());
        }
        for (int i = 0; i < finishCount; i++) {
            automata.getFinishNodes().add(scanner.nextInt());
        }
        return automata;
    }

    private void initDifferentiatedNodes(Automata automata, Queue<Pair<Integer, Integer>> queue,
                                         boolean[][] marked) {
        int n = automata.getSize();
        for (int i = 0; i < n - 1; i++) {
            for (int j = i + 1; j < n; j++) {
                if (automata.getFinishNodes().contains(i) ^ automata.getFinishNodes().contains(j)) {
                    if (reachable[i] && reachable[j]) {
                        queue.add(new Pair<>(i, j));
                        marked[i][j] = true;
                        marked[j][i] = true;
                    }
                }
            }
        }
    }

    static boolean[] reachable;

    static void dfs(Automata automata, int node) {
        reachable[node] = true;
        for (int adj : automata.getAdjacent(node).values()) {
            if (!reachable[adj]) {
                dfs(automata, adj);
            }
        }
    }

    private void markReachable(Automata automata) {
        reachable = new boolean[automata.getSize()];
        dfs(automata, automata.getStartNode());
    }

    private boolean checkEqual(Automata first, Automata second) {
        if ((first.getSize() != second.getSize()) || !first.getAlphabet().equals(second.getAlphabet())) {
            return false;
        }
        Queue<Pair<Integer, Integer>> queue = new LinkedList<>();
        boolean[] usedFirst = new boolean[first.getSize()];
        boolean[] usedSecond = new boolean[second.getSize()];
        queue.add(new Pair<>(first.getStartNode(), second.getStartNode()));
        while (!queue.isEmpty()) {
            int firstNode = queue.peek().first;
            int secondNode = queue.poll().second;
            if (first.getFinishNodes().contains(firstNode) ^ second.getFinishNodes().contains(secondNode)) {
                return false;
            }
            usedFirst[firstNode] = true;
            usedSecond[secondNode] = true;
            for (char c : first.getAlphabet()) {
                if (first.getAdjacent(firstNode).containsKey(c) ^ second.getAdjacent(secondNode).containsKey(c)) {
                    return false;
                }
                if (first.getAdjacent(firstNode).containsKey(c)) {
                    int firstAdj = first.getAdjacent(firstNode).get(c);
                    int secondAdj = second.getAdjacent(secondNode).get(c);
                    if (!usedFirst[firstAdj] || !usedSecond[secondAdj]) {
                        queue.add(new Pair<>(firstAdj, secondAdj));
                    }
                }
            }
        }
        return true;
    }

    private void testAll() throws IOException {
        testCase("tests/sample_input.txt", "tests/sample_correct.txt");
        testCase("tests/single_input.txt", "tests/single_correct.txt");
        testCase("tests/disconnected_input.txt", "tests/disconnected_correct.txt");
        testCase("tests/multiedges_input.txt", "tests/multiedges_correct.txt");
        testCase("tests/random_input.txt", "tests/random_correct.txt");
	System.out.println("Passed all tests.");
    }

    private void testCase(String inputPath, String correctPath) throws IOException {
        Scanner inputScanner = new Scanner(Paths.get(inputPath));
        Map<Integer, Map<Character, List<Integer>>> invertEdges = new HashMap<>();
        Automata inputAutomata = readAutomata(inputScanner, invertEdges);
        Automata outputAutomata = minimizeAutomata(inputAutomata, invertEdges);
        Scanner checkScanner = new Scanner(Paths.get(correctPath));
        Map<Integer, Map<Character, List<Integer>>> correctInvertEdges = new HashMap<>();
        Automata correctAutomata = readAutomata(checkScanner, correctInvertEdges);
        assert checkEqual(outputAutomata, correctAutomata);
    }
}
