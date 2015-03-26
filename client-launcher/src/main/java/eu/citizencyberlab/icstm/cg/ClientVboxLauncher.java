package eu.citizencyberlab.icstm.cg;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferedImage;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.logging.ConsoleHandler;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import javax.imageio.ImageIO;
import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.SwingConstants;
import javax.swing.SwingWorker;
import javax.swing.UIManager;

import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.conn.ssl.AllowAllHostnameVerifier;
import org.apache.http.conn.ssl.SSLContextBuilder;
import org.apache.http.conn.ssl.TrustStrategy;
import org.apache.http.entity.BufferedHttpEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.virtualbox_4_3.AccessMode;
import org.virtualbox_4_3.DeviceType;
import org.virtualbox_4_3.IMachine;
import org.virtualbox_4_3.IMedium;
import org.virtualbox_4_3.IProgress;
import org.virtualbox_4_3.ISession;
import org.virtualbox_4_3.IStorageController;
import org.virtualbox_4_3.IVirtualBox;
import org.virtualbox_4_3.StorageBus;
import org.virtualbox_4_3.StorageControllerType;
import org.virtualbox_4_3.VBoxException;
import org.virtualbox_4_3.VirtualBoxManager;

import net.lingala.zip4j.exception.ZipException;
import net.lingala.zip4j.core.ZipFile;

public class ClientVboxLauncher extends JFrame {

	private static final long serialVersionUID = 2562962395999598807L;

	private static final Logger sLog = Logger
			.getLogger(ClientVboxLauncher.class.getName());

	// ConsoleHandler handler = new ConsoleHandler();
	FileHandler handler;
	// = new FileHandler("pakkachor.log");

	private CGPanel mainPanel = null;
	private CGInfoPanel infoPanel = null;
	private final JProgressBar pb = new JProgressBar(0, 100);

	public ClientVboxLauncher() {
		super("CitizenGrid VirtualBox Launcher");
		this.addWindowListener(new WindowAdapter() {
			@Override
			public void windowClosing(WindowEvent e) {
				System.exit(0);
			}
		});
		try {
			handler = new FileHandler("/tmp/citizengrid_error.log", true);
			handler.setFormatter(new SimpleFormatter());
			handler.setLevel(Level.ALL);
			sLog.addHandler(handler);
		} catch (SecurityException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		// handler.setFormatter(new SimpleFormatter());
		// handler.setLevel(Level.ALL);
		// sLog.addHandler(handler);
		try {
			UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		} catch (Exception e) {
			sLog.severe("ERROR: Unable to set system look and feel.");
		}

		Container content = getContentPane();
		content.setLayout(new BorderLayout());

		mainPanel = new CGPanel();
		infoPanel = new CGInfoPanel();

		content.add(mainPanel, BorderLayout.NORTH);
		content.add(infoPanel, BorderLayout.SOUTH);
		pack();
		setVisible(true);

		infoPanel.setInfoFont(new Font("Arial", Font.PLAIN, 14));
		infoPanel.setDetailFont(new Font("Arial", Font.PLAIN, 14));

		JPanel progressPanel = new JPanel();
		progressPanel.setSize(new Dimension(320, 140));
		progressPanel.setBorder(BorderFactory.createEmptyBorder(10, 5, 10, 5));
		pb.setSize(260, 20);
		progressPanel.add(pb);
		infoPanel.add(progressPanel, BorderLayout.SOUTH);
	}

	class CGPanel extends JPanel {
		BufferedImage image = null;

		public CGPanel() {
			InputStream imageStream = ClientVboxLauncher.class.getClassLoader()
					.getResourceAsStream("logo_trans.png");

			try {
				image = ImageIO.read(imageStream);
			} catch (IOException e) {
				sLog.severe("Unable to to read logo image resource.");
			}
			setPreferredSize(new Dimension(320, 100));
			setBorder(BorderFactory.createLineBorder(Color.gray, 10));
		}

		@Override
		protected void paintComponent(Graphics g) {
			super.paintComponent(g);
			if (image != null) {
				g.drawImage(image, 20, 20, 96, 62, null, null);
				g.setFont(new Font("Arial", Font.PLAIN, 32));
				g.drawString("CitizenGrid", 130, 50);
				g.setFont(new Font("Arial", Font.PLAIN, 17));
				g.drawString("VirtualBox Launcher", 134, 75);
			}
		}
	}

	class CGInfoPanel extends JPanel {
		BufferedImage image = null;
		JLabel infoLabel = null;
		JLabel detailLabel = null;

		public CGInfoPanel() {
			setPreferredSize(new Dimension(320, 140));
			setLayout(new BorderLayout());
			setBorder(BorderFactory
					.createMatteBorder(0, 10, 10, 10, Color.gray));

			infoLabel = new JLabel();
			detailLabel = new JLabel();
			infoLabel.setSize(new Dimension(300, 60));
			detailLabel.setSize(new Dimension(300, 60));
			infoLabel.setBorder(BorderFactory.createLineBorder(
					this.getBackground(), 10));
			detailLabel.setBorder(BorderFactory.createLineBorder(
					this.getBackground(), 10));
			infoLabel.setVerticalAlignment(SwingConstants.CENTER);
			detailLabel.setVerticalAlignment(SwingConstants.CENTER);

			add(infoLabel, BorderLayout.NORTH);
			// add(detailLabel, BorderLayout.SOUTH);
		}

		public void setInfoFont(Font infoFont) {
			infoLabel.setFont(infoFont);
		}

		public void updateInfo(String info) {
			infoLabel.setText(info);
		}

		public void setDetailFont(Font detailFont) {
			detailLabel.setFont(detailFont);
		}

		public void updateDetail(String detail) {
			detailLabel.setText(detail);
		}

		@Override
		protected void paintComponent(Graphics g) {
			super.paintComponent(g);
		}
	}

	private class DownloadFileTask extends SwingWorker<String, Integer> {
		String url = null;

		public DownloadFileTask(String url) {
			this.url = url;
		}

		/**
		 * Unzips the file and returns the uncompressed file path TODO - find
		 * better way to find the unzipped file name and send it back. Currently
		 * it just removes .zip|gz|gzip from file name
		 * 
		 * @throws Exception
		 */
		private String unzipArchivedImage(String archivedImage)
				throws Exception {
			sLog.info("zipped file is \t :" + archivedImage);
			File archivedfile = new File(archivedImage);
			String destination = archivedfile.getParent();
			String unzipFilePath = "";
			try {
				ZipFile zipFile = new ZipFile(archivedfile);
				zipFile.extractAll(destination);
				String ext_pattern = extractFileExtension(archivedImage);
				int idx_pattern = archivedImage.indexOf(ext_pattern);
				
				unzipFilePath = archivedImage.substring(0,idx_pattern);
				sLog.info("unzipped file name is " + unzipFilePath);
				return unzipFilePath;
			} catch (ZipException e) {
				sLog.severe("Cannot unzip archivedImage: Message /t "
						+ e.getMessage());
			}
			return unzipFilePath;
		}

		/**
		 * From SO -
		 * http://stackoverflow.com/questions/617414/create-a-temporary
		 * -directory-in-java
		 * 
		 * @return
		 * @throws IOException
		 */
		@SuppressWarnings("unused")
		public File createTempDirectory() throws IOException {
			final File temp;

			temp = File
					.createTempFile("temp", Long.toString(System.nanoTime()));

			if (!(temp.delete())) {
				throw new IOException("Could not delete temp file: "
						+ temp.getAbsolutePath());
			}

			if (!(temp.mkdir())) {
				throw new IOException("Could not create temp directory: "
						+ temp.getAbsolutePath());
			}

			return (temp);
		}

		@Override
		protected String doInBackground() throws Exception {
			//CloseableHttpClient httpClient = HttpClients.createDefault();
			CloseableHttpClient httpClient = 
					HttpClients.custom().setHostnameVerifier(new AllowAllHostnameVerifier()).
                    setSslcontext(new SSLContextBuilder().
                    loadTrustMaterial(null, new TrustStrategy() {
                        public boolean isTrusted(X509Certificate[] arg0, String arg1) throws CertificateException
                        {
                            return true;
                        }
                    }).build()).build();
			HttpGet getreq = new HttpGet(url);
			CloseableHttpResponse response = null;
			try {
				response = httpClient.execute(getreq);
			} catch (ClientProtocolException e) {
				sLog.severe("Protocol error getting image file: "
						+ e.getMessage());
				return "";
			} catch (IOException e) {
				sLog.severe("Protocol error getting image file: "
						+ e.getMessage());
				return "";
			}

			String tempFileName = null;

			try {
				HttpEntity entity = response.getEntity();
				if (entity != null) {
					long fileSize = entity.getContentLength() == -1 ? Integer.MAX_VALUE
							: entity.getContentLength();

					entity = new BufferedHttpEntity(entity);

					InputStream instream = null;
					try {
						byte buffer[] = new byte[8192];
						instream = new BufferedInputStream(entity.getContent());
						String filename = url.substring(
								url.lastIndexOf('/') + 1, url.length());
						String extn = filename.substring(
								filename.lastIndexOf('.'), filename.length());
						File f = File.createTempFile(filename, extn);
						sLog.info("Writing output data to: " + f.getPath());
						tempFileName = f.getPath();
						FileOutputStream fos = new FileOutputStream(f);

						long totalBytes = 0, byteCount = 0;

						while ((byteCount = instream.read(buffer)) != -1) {
							totalBytes += byteCount;
							sLog.info("Total Bytes is " + totalBytes);
							sLog.info("FileSize is " + fileSize);
							Integer percentComplete = new Integer(
									(int) ((totalBytes * 100) / fileSize));
							// Integer percentComplete = new
							// Long((totalBytes/fileSize)*100).intValue();

							// (totalBytes/fileSize)*100)
							sLog.info("About to publish percent complete: "
									+ percentComplete + "%");
							setProgress(percentComplete);
							fos.write(buffer, 0, (int) byteCount);
						}
						fos.flush();
						fos.close();

					} finally {
						instream.close();
						response.close();
					}
				}
			} catch (IOException e) {
				sLog.severe("Error downloading image data from server: "
						+ e.getMessage());
			} catch (IllegalStateException e) {
				sLog.severe("Error downloading image data from server, illegal state: "
						+ e.getMessage());
			}
			if(extractFileExtension(tempFileName).matches("(.zip)|(.gz)|(.gzip)")){
				return unzipArchivedImage(tempFileName);
			}else{
				return tempFileName;
			}

			

		}

	}

	public CGInfoPanel getInfoPanel() {
		return infoPanel;
	}

	public CGPanel getMainPanel() {
		return mainPanel;
	}

	public JProgressBar getProgressBar() {
		return pb;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {

		if (args.length < 2) {
			printUsage();
			System.exit(0);
		} else {
			sLog.info("Received details for application " + args[0]);
			sLog.info("Received details of " + (args.length - 1) + " images.");
		}

		String appName = args[0];

		for (int i = 1; i < args.length; i++) {
			String urlStr = args[i];
			try {
				URL url = new URL(urlStr);
			} catch (MalformedURLException e) {
				sLog.severe("An invalid URL was provided for image " + (i + 1)
						+ ": " + e.getMessage());
				System.out
						.println("ERROR: An invalid URL was provided for image "
								+ (i + 1) + ": " + e.getMessage());
				printUsage();
				System.exit(0);
			}
		}

		ClientVboxLauncher launcher = new ClientVboxLauncher();
		VirtualBoxManager mgr = VirtualBoxManager.createInstance(null);

		List<String> fileLocations = new ArrayList<String>();

		// Download the files provided as paramters
		for (int i = 1; i < args.length; i++) {
			String urlStr = args[i];
			sLog.info("The file locatio is" + urlStr);
			String fileLocation = launcher.downloadFile(urlStr);
			fileLocations.add(fileLocation);
		}

		// Now check that we can make a connection to the virtualbox
		// web service.
		launcher.getInfoPanel().updateInfo("Connecting to VirtualBox...");

		boolean connectionSuccessful = false;
		while (!connectionSuccessful) {
			try {
				mgr.connect("http://localhost:18083/", "test", "test");
				connectionSuccessful = true;
			} catch (VBoxException e) {
				sLog.severe("Unable to connect to the VirtualBox web service, is it running?");
				int selection = JOptionPane
						.showConfirmDialog(
								launcher,
								"Unable to connect to VirtualBox Web Service. Is it running on your machine?\nWould you like to retry connection?",
								"CitizenGrid Launcher: Unable to connect to VirtualBox",
								JOptionPane.YES_NO_OPTION,
								JOptionPane.ERROR_MESSAGE);
				if (selection == 0) {
					sLog.fine("Retrying connection to VBoxWebSrv...");
				} else if (selection == 1) {
					System.exit(0);
				}
			}
		}

		try {
			String version = mgr.getVBox().getVersion();
			sLog.info("Connected to VirtualBox version " + version);
		} catch (VBoxException e) {
			sLog.severe("Unable to (retrieve VBox version) communicate with the VirtualBox web service, is it running?");
			System.exit(0);
		}

		launcher.getInfoPanel().updateInfo(
				"Registering image with VirtualBox...");

		if (mgr != null) {
			sLog.info("Value of mgr before register: " + mgr.toString());
		} else {
			sLog.info("mgr is NULL before register...");
		}

		// Now we're ready to register our machine with VirtualBox
		// Check if we're registering an OVF or OVA appliance or a standard
		// machine
		// Look through the file extensions
		boolean registerAppliance = false;
		for (String fileLoc : fileLocations) {
			sLog.info(fileLoc);
			sLog.info("size of the file is " + fileLocations.size());

			String extn = extractFileExtension(fileLoc);
			sLog.info("Extension of file <" + fileLoc + "> is <" + extn + ">");
			if (extn.contains("ovf") || extn.contains("ova")) {
				registerAppliance = true;
			}
		}

		IMachine machineId = null;
		if (registerAppliance) {
			// machineId = launcher.vboxRegisterAppliance(mgr, appName,
			// fileLocations); //Need further implementation: TO-DO for
			// supporting ovf and ova images.
		} else {
			machineId = launcher.vboxRegisterMachine(mgr, appName,
					fileLocations);

		}

		if (mgr != null) {
			sLog.info("Value of mgr after register: " + mgr.toString());
		} else {
			sLog.info("mgr is NULL after register...");
		}

		launcher.getInfoPanel().updateInfo(
				"Starting CitizenGrid Application...");

		launcher.vboxRunMachine(mgr, machineId, appName);
		if (mgr != null) {
			sLog.info("Value of mgr after run machine: " + mgr.toString());
		} else {
			sLog.info("mgr is NULL after run machine...");
		}

		mgr.disconnect();
		try {
			mgr.cleanup();
		} catch (NullPointerException e) {
			sLog.warning("\nNull pointer trying to clean up vbox manager");
		}

		mgr = null;
	}

	/**
	 * @param fileLoc
	 * @return
	 */
	private static String extractFileExtension(String fileLoc) {
		return fileLoc.substring(fileLoc.lastIndexOf("."), fileLoc.length());
	}

	public String downloadFile(String filename) {
		DownloadFileTask task = new DownloadFileTask(filename);
		task.addPropertyChangeListener(new PropertyChangeListener() {

			@Override
			public void propertyChange(PropertyChangeEvent e) {
				sLog.info("Property change listener called: "
						+ e.getPropertyName());
				if ("progress".equals(e.getPropertyName())) {
					sLog.info("New progress value: "
							+ (Integer) e.getNewValue() + "%");
					getProgressBar().setValue((Integer) e.getNewValue());
				}
			}
		});

		sLog.info("About to download file...");
		getInfoPanel().updateInfo("Downloading VM Image...");

		task.execute();
		String downloadedFile = null;
		try {
			downloadedFile = task.get();
		} catch (InterruptedException e) {
			sLog.severe("Download worker thread has been interrupted: "
					+ e.getMessage());
		} catch (ExecutionException e) {
			sLog.severe("Error running download worker: " + e.getMessage());
			e.printStackTrace();
		}

		sLog.info("File download has completed. File available at: "
				+ downloadedFile);
		infoPanel.updateInfo("Download Complete...");

		return downloadedFile;

	}

	public IMachine vboxRegisterMachine(VirtualBoxManager mgr, String appName,
			List<String> files) {
		// mgr = VirtualBoxManager.createInstance(null);
		IVirtualBox vbox = mgr.getVBox();

		// FIXME: Need some way of identifying the ordering of disks to connect.
		// For now, we just connect disks assuming that they are listed in order
		// of priority when provided as parameters to the launcher.
		List<String> hds = new ArrayList<String>();
		List<String> cds = new ArrayList<String>();

		String ostype = "Linux";
		for (String filePath : files) {
			String extn = extractFileExtension(filePath);
			if (extn.contains("vdi") || extn.contains("vmdk")
					|| extn.contains("hd")) {
				hds.add(filePath);
				sLog.fine("Will register disk <" + filePath
						+ "> as a hard disk.");
				ostype = setOsType(filePath);
			} else if (extn.contains("iso")) {
				cds.add(filePath);
				sLog.fine("Will register disk <" + filePath + "> as a CD/DVD.");
			} else {
				sLog.warning("Disk <"
						+ filePath
						+ "> is not a recognised type to register as an HD or CD.");
			}
		}

		sLog.info("Initialized connection to VirtualBox version "
				+ vbox.getVersion());

		sLog.info("Creating hard disk object <" + files.get(0) + ">...");

		List<IMedium> hdList = new ArrayList<IMedium>();
		List<IMedium> cdList = new ArrayList<IMedium>();

		for (int i = 0; i < hds.size(); i++) {
			IMedium hd = vbox.openMedium(hds.get(i), DeviceType.HardDisk,
					AccessMode.ReadWrite, false);
			hdList.add(hd);
		}
		for (int i = 0; i < cds.size(); i++) {
			IMedium cd = vbox.openMedium(cds.get(i), DeviceType.DVD,
					AccessMode.ReadOnly, false);
			cdList.add(cd);
		}

		sLog.info("Hard disks and CDs created, creating machine...");

		IMachine machine = vbox.createMachine(null, appName, null, ostype,
				"forceOverwrite=1");
		machine.setMemorySize(512L);
		machine.saveSettings();
		sLog.info("Registering machine...");
		vbox.registerMachine(machine);

		// machine = vbox.findMachine(machineId);
		ISession session = null;
		try {
			session = mgr.openMachineSession(machine);
			machine = session.getMachine();
		} catch (Exception e1) {
			sLog.severe("Unable to open machine session....");
		}

		// Now create the SATA controller and add the hard disks
		sLog.info("Creating SATA storage controller and attaching hard disks to saved machine...");
		IStorageController storage = machine.addStorageController("SATA",
				StorageBus.SATA);
		storage.setControllerType(StorageControllerType.IntelAhci);
		machine.setStorageControllerBootable("SATA", true);
		int controllerPort = 0;
		for (IMedium hd : hdList) {
			machine.attachDevice("SATA", controllerPort, 0,
					DeviceType.HardDisk, hd);
			controllerPort++;
		}

		// FIXME: Need to see if we need to support more than one CD image, at
		// present
		// We can only handle a single image.
		// Now create the IDE controller and add the cd images
		sLog.info("Creating IDE storage controller and attaching cd images to saved machine...");
		if (cdList.size() > 1) {
			throw new org.virtualbox_4_3.VBoxException(
					"Image mount error: Attaching multiple ISO images is not currently supported.");
		}
		machine.addStorageController("IDE", StorageBus.IDE);
		for (IMedium cd : cdList) {
			machine.attachDevice("IDE", 0, 0, DeviceType.DVD, cd);
		}

		machine.setBootOrder(1l, DeviceType.HardDisk);
		machine.saveSettings();
		mgr.closeMachineSession(session);
		return machine;
	}

	/**
	 * sets the ostype of the machine.It currently searches for os string and
	 * sets the machine type based on its type. TODO - Generic algorithm based
	 * on ostype input value
	 * 
	 * @param filePath
	 * @return
	 */
	private String setOsType(String filePath) {
		String ostype;
		ostype = filePath.contains("x86_64") ? "Linux_64" : "Linux";
		return ostype;
	}

	public String vboxRegisterAppliance(VirtualBoxManager mgr, String appName,
			List<String> files) {
		return "";
	}

	public void vboxRunMachine(VirtualBoxManager mgr, IMachine machineId, String appName) {
		System.out.println("\nAttempting to start VM '" + machineId + "'");
		IVirtualBox vbox = mgr.getVBox();
		ISession session = mgr.getSessionObject();
		//sLog.info("We are going to launch: " + machineId.getName());
		for (IMachine mach : vbox.getMachines()) {

			sLog.info("Sessions state " + session.getState().toString());
			sLog.info("Looking at machine: " + mach.getName());
			if(mach.getName().equals(appName)) {
				IProgress p = mach.launchVMProcess(session, "gui", "");
				p.waitForCompletion(10000);	
			}
			else {
				sLog.info("<" + mach.getName() + "> is not our machine continue search...");
			}
			
		}

		session.unlockMachine();

		// mgr.startVm(machineId, null, 7000);
		sLog.info("\nVirtual machine '" + machineId
				+ "' has been started successfully.");
	}

	public void vboxRunExistingMachine(String _name_of_machine_to_start) {
		VirtualBoxManager mgr = VirtualBoxManager.createInstance(null);
		mgr.connect("http://localhost:18083/", "test", "test");
		ISession session = mgr.getSessionObject();
		IVirtualBox vbox = mgr.getVBox();

		System.out.println("Initialized connection to VirtualBox version "
				+ vbox.getVersion());

		List<IMachine> machines = vbox.getMachines();
		for (IMachine machine : machines) {
			sLog.info("Machine name: " + machine.getName());
		}

		// Now we're going to start the Ubuntu 10.04 machine
		IMachine myMachine = null;
		for (IMachine machine : machines) {
			if (machine.getName().equals(_name_of_machine_to_start)) {
				myMachine = machine;
			}
		}
		if (myMachine == null) {
			System.err.println("We couldn't find the required machine...");
			return;
		}

		String m = myMachine.getName();
		System.out.println("\nAttempting to start VM '" + m + "'");
		System.out.println("\nValue of MGR (1)'" + mgr.toString() + "'");
		IProgress p = myMachine.launchVMProcess(session, "gui", "");
		p.waitForCompletion(-1);
		// mgr.startVm(m, null, 7000);
		System.out.println("\nValue of MGR (2)'" + mgr.toString() + "'");
		mgr.disconnect();
		System.out.println("\nValue of MGR (3)'" + mgr.toString() + "'");
		try {
			mgr.cleanup();
		} catch (NullPointerException e) {
			System.out
					.println("\nNull pointer trying to clean up vbox manager");
		}
		System.out.println("\nValue of MGR (4)'" + mgr.toString() + "'");
	}

	public static void printUsage() {
		System.out
				.println("\nUsage: ClientVboxLauncher <Application Name> <HD/CD Image URL> [additional HD/CD Image URLs]");
	}
}
