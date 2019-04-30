package NER;

import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations.AnswerAnnotation;
import edu.stanford.nlp.util.StringUtils;

import java.io.*;
import java.util.*;

public class PeopleNameExtractor {
    static boolean containword(String a, String b) {
        a = a.replaceAll("-", " ");
        b = b.replaceAll("-", " ");
        String[] as = a.split(" ");
        String[] bs = b.split(" ");
        HashSet<String> hs = new HashSet<>(Arrays.asList(as));
        for (String s : bs) {
            if (!hs.contains(s)) return false;
        }
        return true;
    }
    public static void main(String[] args) {
        String serializedClassifier = "/home/karry/NYU/Spring2019/nlp/assignment/project/stanford-ner/" +
                "classifiers/english.all.3class.distsim.crf.ser.gz";

        AbstractSequenceClassifier classifier = CRFClassifier.getClassifierNoExceptions(serializedClassifier);
        String filePath = "/home/karry/NYU/Spring2019/nlp/assignment/project/Stone.txt", fileContents = "";
//        try {
//            InputStreamReader isr = new InputStreamReader(new FileInputStream(filePath),"unicode");
//            BufferedReader br = new BufferedReader(isr);
//            StringBuilder sb = new StringBuilder();
//            String cur;
//            while((cur = br.readLine()) != null) {
//                sb.append(cur);
//                sb.append(' ');
//            }
//            fileContents = sb.toString();
//        } catch (Exception e) {
//            System.out.println(e.getMessage());
//            System.exit(1);
//        }
//
//        List<List<CoreLabel>> out = classifier.classify(fileContents);
//        for (List<CoreLabel> sentence : out) {
//            for (CoreLabel word : sentence) {
//                System.out.print(word.word() + '/' + word.get(AnswerAnnotation.class) + ' ');
//            }
//            System.out.println();
//        }
        Map<String, List<String>> map = new HashMap<>();
        List<List<CoreLabel>> o = classifier.classifyFile(filePath);
        HashSet<String> hs = new HashSet<>();
        StringBuilder sb = new StringBuilder();
        for (List<CoreLabel> sentence : o) {
            for (CoreLabel word : sentence) {
                if (word.get(AnswerAnnotation.class).compareTo("PERSON") == 0) {
                    if (word.word().compareTo("-") == 0) continue;
                    sb.append(word.word().toLowerCase());
                    sb.append(' ');
                }
                else if (sb.length() > 0) {
                    hs.add(sb.toString());
                    sb.setLength(0);
                }
            }
        }
        List<String> ls = new ArrayList<>(hs);
        ls.sort(Collections.reverseOrder());
        DistanceUtil dis = new DistanceUtil();
        // for Jaro
        for (int i = 0; i < ls.size(); i++) {
            for (int j = i + 1; j < ls.size(); j++) {
                double sim = dis.jaro(ls.get(i), ls.get(j));
                if (sim > 0.9 || containword(ls.get(i), ls.get(j))) { // deal with "A B" vs "A"
                    String val = ls.get(j), key = ls.get(i);
                    List<String> list = map.getOrDefault(key, new ArrayList<>());
                    list.add(val);
                    map.put(key, list);
                    ls.remove(j);
                    j--;
                }
            }
        }
//        // for soundex
//        List<String> encoded = new ArrayList<>();
//        hs.clear();
//        for (String s : ls) encoded.add(dis.soundex(s));
//        for (int i = 0; i < ls.size(); i++) {
//            if (!hs.contains(encoded.get(i))) {
//                hs.add(encoded.get(i));
//            }
//            else {
//                ls.remove(i);
//                encoded.remove(i);
//                i--;
//            }
//        }
        try {
            String filename = "/name_jaro.txt";
            BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + filename));
            for (String s : ls) {
                writer.write(s + "\n");
            }
            writer.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
        try {
            String dictname = "/dict.txt";
            BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + dictname));
            for (Map.Entry<String, List<String>> entry : map.entrySet()) {
                String s = entry.getKey().trim();
                for (String val : entry.getValue()) {
                    s += (", " + val.trim());
                }
                String key = entry.getKey().trim().replaceAll(" ", "_").toUpperCase();
                writer.write(key + ": " + s + "\n");
            }
            writer.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}
