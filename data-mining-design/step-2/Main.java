import java.util.List;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;

public class Main {
	public static void main (String ... args) throws Exception {
		
		String project = "apache";
		String outputFile = "results/refactorings_at_" + project + "_prs_level.csv";
		saveToFile(outputFile, getResultAtCommitHeader());
		System.out.println("Refactoring detection at commit level...");
		allCommitsRefactoringDetector("data/commits_to_process.csv", outputFile);
		System.out.println("Refactoring detection at pull request level...");
		prsRefactoringDetector("data/prs_to_process.csv", outputFile);
	}
	
	private static void allCommitsRefactoringDetector(String inputFile, String outputFile) throws IOException {
		
		BufferedReader csvReader = new BufferedReader(new FileReader(inputFile));
		String row = csvReader.readLine();
		while ((row = csvReader.readLine()) != null) {
		    String[] data = row.split(",");
		    refactoringDetectorAtCommit(data[0].replace("www.", ""), data[1], data[2], outputFile); 
		    System.out.println();		    
		}
		csvReader.close();
	}
	
	private static String extractRefactoringTarget(String refactoringName) {
		
		refactoringName = refactoringName.toLowerCase();		
		if (refactoringName.contains("package"))
			return "package";
		else if (refactoringName.contains("folder")) 
			return "folder";
		else if (refactoringName.contains("class"))
			return "class";
		else if (refactoringName.contains("subclass")) 
			return "subclass";
		else if (refactoringName.contains("superclass")) 
			return "superclass";
		else if (refactoringName.contains("interface"))
			return "interface";		
		else if (refactoringName.contains("method"))
			return "method";
		else if (refactoringName.contains("return"))
			return "method";
		else if (refactoringName.contains("attribute"))
			return "attribute";
		else if (refactoringName.contains("parameter"))
			return "parameter";
		else if (refactoringName.contains("variable"))
			return "variable";		
		else 
			return "NA";  
	}
	
	private static String extractRepositoryName(String repoUrl) {
		return repoUrl.substring(18, repoUrl.length() - 4).substring(1); // 19 (https://github.com/) - 4 (.git)
	}
	
	//from RefactoringMiner + additions
	private static String getResultAtCommitHeader() {
		return "repo;pr_number;commit;refactoring_type;refactoring_target;refactoring_detail";
	}

	//from RMiner + additions
	private static String getResultRefactoringDescription(String repoUrl, String prNumber, String commit, Refactoring ref) {
		
		String repoName;
		String refactoringTarget;
		String refactoringDetail;
		
		if (ref != null) {
			repoName = ref.getName();
			refactoringTarget = extractRefactoringTarget(repoName);
			refactoringDetail = ref.toString();
		} else 
			repoName = refactoringTarget = refactoringDetail = "";
				
		StringBuilder builder = new StringBuilder();
		builder.append(extractRepositoryName(repoUrl));
		builder.append(";");
		builder.append(prNumber);
		builder.append(";");
		builder.append(commit);
		builder.append(";");
		builder.append(repoName);
		builder.append(";");
		builder.append(refactoringTarget);
		builder.append(";");
		builder.append(refactoringDetail); //refactoring_detail field		
		return builder.toString();
	}
	
	private static void prsRefactoringDetector(String inputFile, String outputFile) throws NumberFormatException, Exception {

		BufferedReader csvReader = new BufferedReader(new FileReader(inputFile));
		String row = csvReader.readLine();
		while ((row = csvReader.readLine()) != null) {
			String[] data = row.split(",");
			refactoringDetectorAtPR(data[0].replace("www.", ""), Integer.valueOf(data[1]), outputFile); 
			System.out.println();		    
		}
		csvReader.close();
	}

	private static void refactoringDetectorAtCommit(String repo, String pullRequestNumber, String commitId, String outputFile) {
		GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();		
		miner.detectAtCommit(repo, commitId, new RefactoringHandler() {
			@Override
			public void handle(String commitId, List<Refactoring> refactorings) {
				refactoringsHandler(repo, Integer.valueOf(pullRequestNumber), commitId, refactorings, outputFile);
			}
		}, 2000);
	}
	
	private static void refactoringDetectorAtPR(String repo, int pullRequestNumber, String outputFile) throws Exception {

		GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();
		miner.detectAtPullRequest(repo, pullRequestNumber, new RefactoringHandler() {
			@Override
			public void handle(String commitId, List<Refactoring> refactorings) {
				refactoringsHandler(repo, pullRequestNumber, commitId, refactorings, outputFile);	    
			}
		}, 1000);
		System.out.println();
	}
	
	private static void refactoringsHandler(String repo, int pullRequestNumber, String commitId, List<Refactoring> refactorings, String outputFile) {
		
		System.out.println("\n" + refactorings.size() + " refactorings at " + commitId);
		if (refactorings.size() == 0)
			saveToFile(outputFile, getResultRefactoringDescription(repo, String.valueOf(pullRequestNumber), commitId, null));		
		for (Refactoring ref : refactorings) {
			saveToFile(outputFile, getResultRefactoringDescription(repo, String.valueOf(pullRequestNumber), commitId, ref));
			System.out.println(ref.toString()); 
		}
	}

	//from RefactoringMiner
	private static void saveToFile(String fileName, String content) {
		Path path = Paths.get(fileName);
		byte[] contentBytes = (content + System.lineSeparator()).getBytes();
		try {
			Files.write(path, contentBytes, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}		
}
