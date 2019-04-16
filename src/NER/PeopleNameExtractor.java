package NER;

import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations.AnswerAnnotation;
import edu.stanford.nlp.util.StringUtils;

import java.io.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;

public class PeopleNameExtractor {
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
        List<List<CoreLabel>> o = classifier.classifyFile(filePath);
        HashSet<String> hs = new HashSet<>();
        StringBuilder sb = new StringBuilder();
        for (List<CoreLabel> sentence : o) {
            for (CoreLabel word : sentence) {
                if (word.get(AnswerAnnotation.class).compareTo("PERSON") == 0) {
                    sb.append(word.word());
                    sb.append(' ');
                }
                else if (sb.length() > 0) {
                    hs.add(sb.toString());
                    sb.setLength(0);
                }
            }
        }
        List<String> ls = new ArrayList<>(hs);
        Collections.sort(ls);
        DistanceUtil dis = new DistanceUtil();
        for (int i = 0; i < ls.size(); i++) {
            for (int j = i + 1; j < ls.size(); j++) {
                double sim = dis.jaro(ls.get(i), ls.get(j));
                if (sim > 0.9) {
                    ls.remove(j);
                    j--;
                }
            }
        }
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(System.getProperty("user.dir") + "/name_jaro.txt"));
            for (String s : ls) {
                writer.write(s + "\n");
            }
            writer.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}
