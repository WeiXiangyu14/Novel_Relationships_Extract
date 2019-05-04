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
        // return whether a contains b
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

        Map<String, List<String>> map = new HashMap<>();
        List<List<CoreLabel>> o = classifier.classifyFile(filePath);
        // HashSet<String> hs = new HashSet<>(), male = new HashSet<>(), female = new HashSet<>();
        HashMap<String, Integer> names = new HashMap<>();
        StringBuilder sb = new StringBuilder();
        for (List<CoreLabel> sentence : o) {
            String prefix = "";
            for (int i = 0; i < sentence.size(); i++) {
                CoreLabel word = sentence.get(i);
                if (word.get(AnswerAnnotation.class).compareTo("PERSON") == 0) {
//                    if (i > 0 && sentence.get(i - 1).get(AnswerAnnotation.class).compareTo("PERSON") != 0) {
//                        String mr = sentence.get(i - 1).word().toLowerCase();
//                        if (mr.compareTo("mr") == 0 || mr.compareTo("mrs") == 0 ||
//                                mr.compareTo("mr.") == 0 || mr.compareTo("mrs.") == 0) {
//                            prefix = mr;
//                        }
//                    }
                    String w = word.word();
                    if (Character.isLetter(w.charAt(0)) && w.charAt(1) == '.') continue;
                    if (w.compareTo("-") == 0) continue;
                    sb.append(w.toLowerCase());
                    sb.append(' ');
                }
                else if (sb.length() > 0) {
//                    if (prefix.compareTo("mr") == 0 || prefix.compareTo("mr.") == 0) {
//                        male.add(sb.toString());
//                    }
//                    if (prefix.compareTo("mrs") == 0 || prefix.compareTo("mrs.") == 0) {
//                        female.add(sb.toString());
//                    }
                    String t = sb.toString().trim();
                    names.put(t, names.getOrDefault(t, 0) + 1);
                    sb.setLength(0);
                }
            }
        }
        List<String> ls = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : names.entrySet()) {
            if (entry.getValue() > 3) ls.add(entry.getKey());
        }
        ls.sort(Collections.reverseOrder());
        DistanceUtil dis = new DistanceUtil();
        HashSet<String> fname = new HashSet<>();
        for (String s : ls) {
            int count = 0;
            for (String v : ls) {
                if (s.equals(v)) continue;
                if (containword(v, s)) count++;
            }
            if (count == 1) fname.add(s);
        }
        // for Jaro
        for (int i = 0; i < ls.size(); i++) {
            boolean inmap = false;
            for (int j = i + 1; j < ls.size(); j++) {
                double sim = dis.jaro(ls.get(i), ls.get(j));
                if (sim > 0.9 || fname.contains(ls.get(j)) && containword(ls.get(i), ls.get(j))) { // deal with "A B" vs "A"
                    String val = ls.get(j), key = ls.get(i);
                    List<String> list = map.getOrDefault(key, new ArrayList<>());
                    list.add(val);
                    map.put(key, list);
                    ls.remove(j);
                    j--;
                    inmap = true;
                }
            }
            if (!inmap) {
                List<String> l = new ArrayList<>();
                map.put(ls.get(i), l);
            }
        }
        Iterator<String> it = map.keySet().iterator();
        while (it.hasNext()) {
            String s = it.next();
            int count = 0;
            for (String t : map.get(s)) {
                count += names.get(t);
            }
            count += names.get(s);
            if (count < 5) it.remove();
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
            String dictname = "/dict_highfreq.txt";
            BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + dictname));
            for (Map.Entry<String, List<String>> entry : map.entrySet()) {
                String s = entry.getKey().trim(), key = s;
                for (String val : entry.getValue()) {
//                    String t;
//                    if (female.contains(val)) {
//                        t = "Mrs. " + val.trim();
//                        key = t;
//                    }
//                    else if (male.contains(val)) {
//                        t = "Mr. " + val.trim();
//                        key = t;
//                    }
//                    else {
//                        t = val.trim();
//                    }
                    s += (", " + val.trim());
                }
                key = key.replaceAll(" ", "_").toUpperCase();
                writer.write(key + ": " + s + "\n");
            }
            writer.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}
